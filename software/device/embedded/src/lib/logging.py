import sys
import time
from util.time import isoformat


CRITICAL = 50
ERROR = 40
WARNING = 30
INFO = 20
DEBUG = 10
NOTSET = 0

_level_dict = {
    CRITICAL: "CRIT",
    ERROR: "ERROR",
    WARNING: "WARN",
    INFO: "INFO",
    DEBUG: "DEBUG",
}


class MultiStream:
    def __init__(self):
        self.repl = sys.stderr
        self.file = None

    def set_file(self, file):
        self.unset_file()
        self.file = open(file, "a+")

    def unset_file(self):
        if self.file:
            self.file.close()
        self.file = None

    def write(self, msg):
        if self.repl:
            self.repl.write(msg)
        if self.file:
            self.file.write(msg)

    def flush(self):
        # stderr cannot be flushed
        if self.file:
            self.file.flush()


_stream = MultiStream()


class Logger:

    level = NOTSET

    def __init__(self, name):
        self.name = name

    def _level_str(self, level):
        l = _level_dict.get(level)
        if l is not None:
            return l
        return "LVL%s" % level

    def setLevel(self, level):
        self.level = level

    def isEnabledFor(self, level):
        return level >= (self.level or _level)

    def log(self, level, msg, *args):
        msg = str(msg)
        datestamp = "{0}".format(isoformat(time.localtime(), sep=" "))
        if level >= (self.level or _level):
            _stream.write(
                "{:19s}  {:5s}  {}: ".format(
                    datestamp, self._level_str(level), self.name
                )
            )
            if not args:
                _stream.write("{}\n".format(msg))
            else:
                _stream.write("{}\n".format(msg % args))
            # Flush the file stream
            _stream.flush()

    def debug(self, msg, *args):
        self.log(DEBUG, msg, *args)

    def info(self, msg, *args):
        self.log(INFO, msg, *args)

    def warning(self, msg, *args):
        self.log(WARNING, msg, *args)

    def error(self, msg, *args):
        self.log(ERROR, msg, *args)

    def critical(self, msg, *args):
        self.log(CRITICAL, msg, *args)


_level = INFO
_loggers = {}


def getLogger(name):
    if name in _loggers:
        return _loggers[name]
    l = Logger(name)
    _loggers[name] = l
    return l


def info(msg, *args):
    getLogger(None).info(msg, *args)


def debug(msg, *args):
    getLogger(None).debug(msg, *args)


def basicConfig(level=INFO, filename=None, stream=None, format=None):
    global _level, _stream
    _level = level
    if stream:
        _stream = stream
    if filename is not None:
        print("logging.basicConfig: filename arg is not supported")
    if format is not None:
        print("logging.basicConfig: format arg is not supported")
