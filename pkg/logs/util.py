import inspect
import os.path


def get_caller_info() -> str:
    caller = inspect.getframeinfo(inspect.stack()[3][0])
    return f"{os.path.split(caller.filename)[-1]}:{caller.lineno}"
