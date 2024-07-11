import logging
from typing import AnyStr, LiteralString

_DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s"


def debug(msg: object):
    logging.debug(msg=msg, stacklevel=2)


def info(msg: object):
    logging.info(msg=msg, stacklevel=2)


def warning(msg: object):
    logging.warning(msg=msg, stacklevel=2)


def error(msg: object):
    logging.error(msg=msg, stacklevel=2)


def init(filename: AnyStr | LiteralString | None = None, level: int = logging.DEBUG):
    logging.basicConfig(
        filename=filename,
        level=level,
        format=_DEFAULT_FORMAT,
    )
