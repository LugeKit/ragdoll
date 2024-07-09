import enum
from datetime import datetime
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

    @staticmethod
    def _fmt_print(log_level_str: str, caller_info: str, msg: LiteralString | AnyStr):
        t = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[{log_level_str}] [{t}] {caller_info}: {msg}")

    def debug(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.DEBUG:
            return
        self._fmt_print("DEBUG", util.get_caller_info(), msg)

    def info(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.INFO:
            return
        self._fmt_print("INFO", util.get_caller_info(), msg)

    def warn(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.WARNING:
            return
        self._fmt_print("WARN", util.get_caller_info(), msg)

    def error(self, msg: LiteralString | AnyStr):
        if self.log_level > LogLevel.ERROR:
            return
        self._fmt_print("ERROR", util.get_caller_info(), msg)


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
