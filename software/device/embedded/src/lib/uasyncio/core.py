# uasyncio.core fast_io
# (c) 2014-2018 Paul Sokolovsky. MIT license.

# This is a fork of official MicroPython uasynco. It is recommended to use
# the official version unless the specific features of this fork are required.

# Changes copyright (c) Peter Hinch 2018, 2019
# Code at https://github.com/peterhinch/micropython-async.git
# fork: peterhinch/micropython-lib branch: uasyncio-io-fast-and-rw

version = ("fast_io", "0.26")
try:
    import rtc_time as time  # Low power timebase using RTC
except ImportError:
    import utime as time
import utimeq
import ucollections


type_gen = type((lambda: (yield))())
type_genf = type((lambda: (yield)))  # Type of a generator function upy iss #3241

DEBUG = 0
log = None


def set_debug(val):
    global DEBUG, log
    DEBUG = val
    if val:
        import logging

        log = logging.getLogger("uasyncio.core")


class CancelledError(Exception):
    pass


class TimeoutError(CancelledError):
    pass


class EventLoop:
    def __init__(self, runq_len=16, waitq_len=16, ioq_len=0, lp_len=0):
        self.runq = ucollections.deque((), runq_len, True)
        self._max_od = 0
        self.lpq = utimeq.utimeq(lp_len) if lp_len else None
        self.ioq_len = ioq_len
        self.canned = set()
        if ioq_len:
            self.ioq = ucollections.deque((), ioq_len, True)
            self._call_io = self._call_now
        else:
            self._call_io = self.call_soon
        self.waitq = utimeq.utimeq(waitq_len)
        # Current task being run. Task is a top-level coroutine scheduled
        # in the event loop (sub-coroutines executed transparently by
        # yield from/await, event loop "doesn't see" them).
        self.cur_task = None

    def time(self):
        return time.ticks_ms()

    def create_task(self, coro):
        # CPython 3.4.2
        assert not isinstance(
            coro, type_genf
        ), "Coroutine arg expected."  # upy issue #3241
        # create_task with a callable would work, so above assert only traps the easily-made error
        self.call_later_ms(0, coro)
        # CPython asyncio incompatibility: we don't return Task object

    def _call_now(self, callback, *args):  # For stream I/O only
        if __debug__ and DEBUG:
            log.debug("Scheduling in ioq: %s", (callback, args))
        self.ioq.append(callback)
        if not isinstance(callback, type_gen):
            self.ioq.append(args)

    def max_overdue_ms(self, t=None):
        if t is not None:
            self._max_od = int(t)
        return self._max_od

    # Low priority versions of call_later() call_later_ms() and call_at_()
    def call_after_ms(self, delay, callback, *args):
        self.call_at_lp_(time.ticks_add(self.time(), delay), callback, *args)

    def call_after(self, delay, callback, *args):
        self.call_at_lp_(
            time.ticks_add(self.time(), int(delay * 1000)), callback, *args
        )

    def call_at_lp_(self, time, callback, *args):
        if self.lpq is not None:
            self.lpq.push(time, callback, args)
            if isinstance(callback, type_gen):
                callback.pend_throw(id(callback))
        else:
            raise OSError("No low priority queue exists.")

    def call_soon(self, callback, *args):
        if __debug__ and DEBUG:
            log.debug("Scheduling in runq: %s", (callback, args))
        self.runq.append(callback)
        if not isinstance(callback, type_gen):
            self.runq.append(args)

    def call_later(self, delay, callback, *args):
        self.call_at_(time.ticks_add(self.time(), int(delay * 1000)), callback, args)

    def call_later_ms(self, delay, callback, *args):
        if not delay:
            return self.call_soon(callback, *args)
        self.call_at_(time.ticks_add(self.time(), delay), callback, args)

    def call_at_(self, time, callback, args=()):
        if __debug__ and DEBUG:
            log.debug("Scheduling in waitq: %s", (time, callback, args))
        self.waitq.push(time, callback, args)
        if isinstance(callback, type_gen):
            callback.pend_throw(id(callback))

    def wait(self, delay):
        # Default wait implementation, to be overriden in subclasses
        # with IO scheduling
        if __debug__ and DEBUG:
            log.debug("Sleeping for: %s", delay)
        time.sleep_ms(delay)

    def run_forever(self):
        cur_task = [0, 0, 0]
        # Put a task on the runq unless it was cancelled
        def runq_add():
            if isinstance(cur_task[1], type_gen):
                tid = id(cur_task[1])
                if tid in self.canned:
                    self.canned.remove(tid)
                else:
                    cur_task[1].pend_throw(None)
                    self.call_soon(cur_task[1], *cur_task[2])
            else:
                self.call_soon(cur_task[1], *cur_task[2])

        while True:
            # Expire entries in waitq and move them to runq
            tnow = self.time()
            if self.lpq:
                # Schedule a LP task if overdue or if no normal task is ready
                to_run = False  # Assume no LP task is to run
                t = self.lpq.peektime()
                tim = time.ticks_diff(t, tnow)
                to_run = self._max_od > 0 and tim < -self._max_od
                if not (to_run or self.runq):  # No overdue LP task or task on runq
                    # zero delay tasks go straight to runq. So don't schedule LP if runq
                    to_run = tim <= 0  # True if LP task is due
                    if to_run and self.waitq:  # Set False if normal tasks due.
                        t = self.waitq.peektime()
                        to_run = time.ticks_diff(t, tnow) > 0  # No normal task is ready
                if to_run:
                    self.lpq.pop(cur_task)
                    runq_add()

            while self.waitq:
                t = self.waitq.peektime()
                delay = time.ticks_diff(t, tnow)
                if delay > 0:
                    break
                self.waitq.pop(cur_task)
                if __debug__ and DEBUG:
                    log.debug("Moving from waitq to runq: %s", cur_task[1])
                runq_add()

            # Process runq. This can append tasks to the end of .runq so get initial
            # length so we only process those items on the queue at the start.
            l = len(self.runq)
            if __debug__ and DEBUG:
                log.debug("Entries in runq: %d", l)
            cur_q = self.runq  # Default: always get tasks from runq
            dl = 1  # Subtract this from entry count l
            while l or self.ioq_len:
                if self.ioq_len:  # Using fast_io
                    self.wait(0)  # Schedule I/O. Can append to ioq.
                    if self.ioq:
                        cur_q = self.ioq
                        dl = 0  # No effect on l
                    elif l == 0:
                        break  # Both queues are empty
                    else:
                        cur_q = self.runq
                        dl = 1
                l -= dl
                cb = cur_q.popleft()  # Remove most current task
                args = ()
                if not isinstance(
                    cb, type_gen
                ):  # It's a callback not a generator so get args
                    args = cur_q.popleft()
                    l -= dl
                    if __debug__ and DEBUG:
                        log.info("Next callback to run: %s", (cb, args))
                    cb(*args)  # Call it
                    continue  # Proceed to next runq entry

                if __debug__ and DEBUG:
                    log.info("Next coroutine to run: %s", (cb, args))
                self.cur_task = cb  # Stored in a bound variable for TimeoutObj
                delay = 0
                low_priority = False  # Assume normal priority
                try:
                    if args is ():
                        ret = next(cb)  # Schedule the coro, get result
                    else:
                        ret = cb.send(*args)
                    if __debug__ and DEBUG:
                        log.info("Coroutine %s yield result: %s", cb, ret)
                    if isinstance(
                        ret, SysCall1
                    ):  # Coro returned a SysCall1: an object with an arg spcified in its constructor
                        arg = ret.arg
                        if isinstance(ret, SleepMs):
                            delay = arg
                            if isinstance(ret, AfterMs):
                                low_priority = True
                                if isinstance(ret, After):
                                    delay = int(delay * 1000)
                        elif isinstance(
                            ret, IORead
                        ):  # coro was a StreamReader read method
                            cb.pend_throw(
                                False
                            )  # Marks the task as waiting on I/O for cancellation/timeout
                            # If task is cancelled or times out, it is put on runq to process exception.
                            # Debug note: if task is scheduled other than by wait (which does pend_throw(None)
                            # an exception (exception doesn't inherit from Exception) is thrown
                            self.add_reader(
                                arg, cb
                            )  # Set up select.poll for read and store the coro in object map
                            continue  # Don't reschedule. Coro is scheduled by wait() when poll indicates h/w ready
                        elif isinstance(
                            ret, IOWrite
                        ):  # coro was StreamWriter.awrite. Above comments apply.
                            cb.pend_throw(False)
                            self.add_writer(arg, cb)
                            continue
                        elif isinstance(
                            ret, IOReadDone
                        ):  # update select.poll registration and if necessary remove coro from map
                            self.remove_reader(arg)
                            self._call_io(
                                cb, args
                            )  # Next call produces StopIteration enabling result to be returned
                            continue
                        elif isinstance(ret, IOWriteDone):
                            self.remove_writer(arg)
                            self._call_io(
                                cb, args
                            )  # Next call produces StopIteration: see StreamWriter.aclose
                            continue
                        elif isinstance(
                            ret, StopLoop
                        ):  # e.g. from run_until_complete. run_forever() terminates
                            return arg
                        else:
                            assert False, "Unknown syscall yielded: %r (of type %r)" % (
                                ret,
                                type(ret),
                            )
                    elif isinstance(
                        ret, type_gen
                    ):  # coro has yielded a coro (or generator)
                        self.call_soon(ret)  # append to .runq
                    elif isinstance(ret, int):  # If coro issued yield N, delay = N ms
                        delay = ret
                    elif ret is None:
                        # coro issued yield. delay == 0 so code below will put the current task back on runq
                        pass
                    elif ret is False:
                        # yield False causes coro not to be rescheduled i.e. it stops.
                        continue
                    else:
                        assert (
                            False
                        ), "Unsupported coroutine yield value: %r (of type %r)" % (
                            ret,
                            type(ret),
                        )
                except StopIteration as e:
                    if __debug__ and DEBUG:
                        log.debug("Coroutine finished: %s", cb)
                    continue
                except CancelledError as e:
                    if __debug__ and DEBUG:
                        log.debug("Coroutine cancelled: %s", cb)
                    continue
                # Currently all syscalls don't return anything, so we don't
                # need to feed anything to the next invocation of coroutine.
                # If that changes, need to pass that value below.
                if low_priority:
                    self.call_after_ms(delay, cb)  # Put on lpq
                elif delay:
                    self.call_later_ms(delay, cb)
                else:
                    self.call_soon(cb)

            # Wait until next waitq task or I/O availability
            delay = 0
            if not self.runq:
                delay = -1
                if self.waitq:
                    tnow = self.time()
                    t = self.waitq.peektime()
                    delay = time.ticks_diff(t, tnow)
                    if delay < 0:
                        delay = 0
                if self.lpq:
                    t = self.lpq.peektime()
                    lpdelay = time.ticks_diff(t, tnow)
                    if lpdelay < 0:
                        lpdelay = 0
                    if lpdelay < delay or delay < 0:
                        delay = lpdelay  # waitq is empty or lp task is more current
            self.wait(delay)

    def run_until_complete(self, coro):
        assert not isinstance(
            coro, type_genf
        ), "Coroutine arg expected."  # upy issue #3241

        def _run_and_stop():
            ret = (
                yield from coro
            )  # https://github.com/micropython/micropython-lib/pull/270
            yield StopLoop(ret)

        self.call_soon(_run_and_stop())
        return self.run_forever()

    def stop(self):
        self.call_soon((lambda: (yield StopLoop(0)))())

    def close(self):
        pass


class SysCall:
    def __init__(self, *args):
        self.args = args

    def handle(self):
        raise NotImplementedError


# Optimized syscall with 1 arg
class SysCall1(SysCall):
    def __init__(self, arg):
        self.arg = arg


class StopLoop(SysCall1):
    pass


class IORead(SysCall1):
    pass


class IOWrite(SysCall1):
    pass


class IOReadDone(SysCall1):
    pass


class IOWriteDone(SysCall1):
    pass


_event_loop = None
_event_loop_class = EventLoop


def get_event_loop(runq_len=16, waitq_len=16, ioq_len=0, lp_len=0):
    global _event_loop
    if _event_loop is None:
        _event_loop = _event_loop_class(runq_len, waitq_len, ioq_len, lp_len)
    return _event_loop


# Allow user classes to determine prior event loop instantiation.
def get_running_loop():
    if _event_loop is None:
        raise RuntimeError("Event loop not instantiated")
    return _event_loop


def got_event_loop():  # Kept to avoid breaking code
    return _event_loop is not None


def sleep(secs):
    yield int(secs * 1000)


# Implementation of sleep_ms awaitable with zero heap memory usage
class SleepMs(SysCall1):
    def __init__(self):
        self.v = None
        self.arg = None

    def __call__(self, arg):
        self.v = arg
        # print("__call__")
        return self

    def __iter__(self):
        # print("__iter__")
        return self

    def __next__(self):
        if self.v is not None:
            # print("__next__ syscall enter")
            self.arg = self.v
            self.v = None
            return self
        # print("__next__ syscall exit")
        _stop_iter.__traceback__ = None
        raise _stop_iter


_stop_iter = StopIteration()
sleep_ms = SleepMs()


def cancel(coro):
    prev = coro.pend_throw(CancelledError())
    if prev is False:  # Waiting on I/O. Not on q so put it there.
        _event_loop._call_io(coro)
    elif isinstance(prev, int):  # On waitq or lpq
        # task id
        _event_loop.canned.add(prev)  # Alas this allocates
        _event_loop._call_io(coro)  # Put on runq/ioq
    else:
        assert prev is None


class TimeoutObj:
    def __init__(self, coro):
        self.coro = coro


def wait_for_ms(coro, timeout):
    def waiter(coro, timeout_obj):
        res = yield from coro
        if __debug__ and DEBUG:
            log.debug("waiter: cancelling %s", timeout_obj)
        timeout_obj.coro = None
        return res

    def timeout_func(timeout_obj):
        if timeout_obj.coro:
            if __debug__ and DEBUG:
                log.debug("timeout_func: cancelling %s", timeout_obj.coro)
            prev = timeout_obj.coro.pend_throw(TimeoutError())
            if prev is False:  # Waiting on I/O
                _event_loop._call_io(timeout_obj.coro)
            elif isinstance(prev, int):  # On waitq or lpq
                # prev==task id
                _event_loop.canned.add(prev)  # Alas this allocates
                _event_loop._call_io(timeout_obj.coro)  # Put on runq/ioq
            else:
                assert prev is None

    timeout_obj = TimeoutObj(_event_loop.cur_task)
    _event_loop.call_later_ms(timeout, timeout_func, timeout_obj)
    return (yield from waiter(coro, timeout_obj))


def wait_for(coro, timeout):
    return wait_for_ms(coro, int(timeout * 1000))


def coroutine(f):
    return f


# Low priority
class AfterMs(SleepMs):
    pass


class After(AfterMs):
    pass


after_ms = AfterMs()
after = After()

#
# The functions below are deprecated in uasyncio, and provided only
# for compatibility with CPython asyncio
#


def ensure_future(coro, loop=_event_loop):
    _event_loop.call_soon(coro)
    # CPython asyncio incompatibility: we don't return Task object
    return coro


# CPython asyncio incompatibility: Task is a function, not a class (for efficiency)
def Task(coro, loop=_event_loop):
    # Same as async()
    _event_loop.call_soon(coro)
