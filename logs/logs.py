from typing import LiteralString, AnyStr


class _Log:
    def info(self, msg: LiteralString | AnyStr):
        print(msg)


_log_instance = _Log()

info = _log_instance.info
