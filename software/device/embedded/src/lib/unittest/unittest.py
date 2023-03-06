import sys

try:
    import io
except ImportError:
    import uio as io


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class SkipTest(Exception):
    pass


class AssertRaisesContext:
    def __init__(self, exc, msg=None):
        self.expected = exc
        self.expected_message = msg
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is None:
            assert False, "%r not raised" % self.expected
        if issubclass(exc_type, self.expected):
            if self.expected_message is None or str(exc_value) == self.expected_message:
                self.exception = exc_value
                return True
        return False


class TestCase:
    def fail(self, msg=""):
        assert False, msg

    def assertEqual(self, x, y, msg=""):
        if not msg:
            msg = "%r vs (expected) %r" % (x, y)
        assert x == y, msg

    def assertNotEqual(self, x, y, msg=""):
        if not msg:
            msg = "%r not expected to be equal %r" % (x, y)
        assert x != y, msg

    def assertAlmostEqual(self, x, y, places=None, msg="", delta=None):
        if x == y:
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if abs(x - y) <= delta:
                return
            if not msg:
                msg = "%r != %r within %r delta" % (x, y, delta)
        else:
            if places is None:
                places = 7
            if round(abs(y - x), places) == 0:
                return
            if not msg:
                msg = "%r != %r within %r places" % (x, y, places)

        assert False, msg

    def assertNotAlmostEqual(self, x, y, places=None, msg="", delta=None):
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if not (x == y) and abs(x - y) > delta:
                return
            if not msg:
                msg = "%r == %r within %r delta" % (x, y, delta)
        else:
            if places is None:
                places = 7
            if not (x == y) and round(abs(y - x), places) != 0:
                return
            if not msg:
                msg = "%r == %r within %r places" % (x, y, places)

        assert False, msg

    def assertIs(self, x, y, msg=""):
        if not msg:
            msg = "%r is not %r" % (x, y)
        assert x is y, msg

    def assertIsNot(self, x, y, msg=""):
        if not msg:
            msg = "%r is %r" % (x, y)
        assert x is not y, msg

    def assertIsNone(self, x, msg=""):
        if not msg:
            msg = "%r is not None" % x
        assert x is None, msg

    def assertIsNotNone(self, x, msg=""):
        if not msg:
            msg = "%r is None" % x
        assert x is not None, msg

    def assertTrue(self, x, msg=""):
        if not msg:
            msg = "Expected %r to be True" % x
        assert x, msg

    def assertFalse(self, x, msg=""):
        if not msg:
            msg = "Expected %r to be False" % x
        assert not x, msg

    def assertIn(self, x, y, msg=""):
        if not msg:
            msg = "Expected %r to be in %r" % (x, y)
        assert x in y, msg

    def assertIsInstance(self, x, y, msg=""):
        assert isinstance(x, y), msg

    def assertRaises(self, exc, func=None, *args, **kwargs):
        msg = kwargs.get("msg", None)
        if func is None:
            return AssertRaisesContext(exc, msg=msg)

        expected_not_raised = False
        try:
            func(*args, **kwargs)
            expected_not_raised = True

        except Exception as e:
            if isinstance(e, exc):
                if msg is not None:
                    self.assertEqual(str(e), msg)
                return
            print(type(e), "is not type of ", type(exc))
            raise

        if expected_not_raised:
            raise Exception(str(exc) + " not raised")


def skip(msg):
    def _decor(fun):
        # We just replace original fun with _inner
        def _inner(self):
            raise SkipTest(msg)

        return _inner

    return _decor


def skipIf(cond, msg):
    if not cond:
        return lambda x: x
    return skip(msg)


def skipUnless(cond, msg):
    if cond:
        return lambda x: x
    return skip(msg)


class TestSuite:
    def __init__(self):
        self.tests = []

    def addTest(self, cls):
        self.tests.append(cls)


class TestRunner:
    def run(self, suite):
        res = TestResult()
        for c in suite.tests:
            res.exceptions.extend(run_class(c, res))

        print("Ran %d tests\n" % res.testsRun)
        if res.failuresNum > 0 or res.errorsNum > 0:
            print(
                bcolors.FAIL
                + "FAILED "
                + bcolors.ENDC
                + "(failures=%d, errors=%d) " % (res.failuresNum, res.errorsNum)
            )
        else:
            msg = "OK"
            color = bcolors.OKGREEN
            if res.skippedNum > 0:
                msg += " (%d skipped)" % res.skippedNum
                color = bcolors.WARNING
            print(color + msg + bcolors.ENDC)

        return res


class TestResult:
    def __init__(self):
        self.errorsNum = 0
        self.failuresNum = 0
        self.skippedNum = 0
        self.testsRun = 0
        self.exceptions = []

    def wasSuccessful(self):
        return self.errorsNum == 0 and self.failuresNum == 0


if hasattr(sys, "print_exception"):
    print_exception = sys.print_exception
else:
    import traceback

    print_exception = lambda e, f: traceback.print_exception(
        None, e, sys.exc_info()[2], file=f
    )


def capture_exc(name, e):
    buf = io.StringIO()
    buf.write("Exception in: %s\n" % name)
    print_exception(e, buf)
    return buf.getvalue()


# TODO: Uncompliant
def run_class(c, test_result):
    o = c()
    set_up = getattr(o, "setUp", lambda *_: None)
    tear_down = getattr(o, "tearDown", lambda *_: None)
    exceptions = []
    # Any arguments passed to unit test run script will be used as a string match filter on tests
    test_filter = sys.argv[1:]
    for name in dir(o):
        if test_filter:
            if not any([(f == name) for f in test_filter]):
                continue
        if name.startswith("test"):
            print(
                "\n%s%s (%s) ...%s"
                % (bcolors.HEADER, name, c.__qualname__, bcolors.ENDC),
                end="",
            )
            m = getattr(o, name)
            try:
                set_up(name)
            except TypeError:
                set_up()
            try:
                test_result.testsRun += 1
                m()
                print(bcolors.OKGREEN + " ok" + bcolors.ENDC)
            except SkipTest as e:
                print("%s skipped: %s%s" % (bcolors.WARNING, e.args[0], bcolors.ENDC))
                test_result.skippedNum += 1
            except Exception as ex:
                trace = capture_exc(name, ex)
                exceptions.append(trace)
                print("%sfail in %s: %s%s" % (bcolors.FAIL, name, ex, bcolors.ENDC))
                print(trace)
                test_result.failuresNum += 1
                # Uncomment to investigate failure in detail
                # raise
                continue
            finally:
                try:
                    tear_down(name)
                except TypeError:
                    tear_down()
    return exceptions


def main(module="__main__", noexit=False):
    def test_cases(m):
        for tn in dir(m):
            c = getattr(m, tn)
            if (
                isinstance(c, object)
                and isinstance(c, type)
                and issubclass(c, TestCase)
            ):
                yield c

    try:
        m = __import__(module) if isinstance(module, str) else module

    except ImportError as ex:
        print(bcolors.FAIL + "FAILED " + bcolors.ENDC)
        exceptions = [capture_exc(ex)]
        ret = -1

    else:
        suite = TestSuite()
        for c in test_cases(m):
            suite.addTest(c)
        runner = TestRunner()
        result = runner.run(suite)
        exceptions = result.exceptions
        ret = 1 if result.failuresNum else 0

    if exceptions:
        sep = "\n-------------------------------\n"
        print(sep)
        print(sep.join(exceptions))
    # return non zero return code in case of failures

    if noexit:
        return ret
    sys.exit(ret)
