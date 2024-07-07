import enum
from typing import LiteralString, AnyStr

from . import util


class LogLevel(enum.IntEnum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class _Log:
    def __init__(self):
        self.log_level = LogLevel.DEBUG

    def debug(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.DEBUG:
            return
        print(f"[DEBUG] {util.get_caller_info()}: {msg}")

    def info(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.INFO:
            return
        print(f"[INFO] {util.get_caller_info()}: {msg}")

    def warn(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.WARNING:
            return
        print(f"[WARN] {util.get_caller_info()}: {msg}")

    def error(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.ERROR:
            return
        print(f"[ERROR] {util.get_caller_info()}: {msg}")


_log_instance = _Log()


def init(log_level: LogLevel):
    _log_instance.log_level = log_level


def info(msg: LiteralString | AnyStr):
    _log_instance.info(msg)


def debug(msg: LiteralString | AnyStr):
    _log_instance.info(msg)


def warn(msg: LiteralString | AnyStr):
    _log_instance.info(msg)


def error(msg: LiteralString | AnyStr):
    _log_instance.info(msg)
