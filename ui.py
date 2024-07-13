import os
import subprocess
import sys
from typing import override, LiteralString, AnyStr

from watchdog import observers, events
from watchdog.events import FileSystemEvent

from pkg import logs

Str = AnyStr | LiteralString


class UiPyManager:
    def __init__(self, dir_path: Str):
        self.dir_path = dir_path

    @staticmethod
    def _get_filename_from_path(filepath: Str) -> str:
        filename = filepath.split(os.sep)[-1]
        return filename.split('.')[0]

    def create(self, ui_filepath: Str):
        py_filepath = self._py_filepath(ui_filepath)
        args = ["pyside6-uic", ui_filepath, "-o", py_filepath]
        try:
            subprocess.call(args)
            logs.info(f"create {py_filepath} successfully")
            with open(os.sep.join([self.dir_path, "__init__.py"]), "a") as f:
                f.write(f"from . import {self._get_filename_from_path(py_filepath)}\n")

        except Exception as e:
            logs.error(f"failed to create {ui_filepath}: {e}")

    def clear(self):
        logs.info(f"clear all file in {self.dir_path}")
        for (_, _, files) in os.walk(self.dir_path):
            for file in files:
                if file.endswith("pyc"):
                    continue

                try:
                    os.remove(os.sep.join([self.dir_path, file]))
                except Exception as e:
                    logs.error(f"failed to delete {file}: {e}")

    def _py_filepath(self, ui_filepath: Str) -> str:
        py_filename = f"{self._get_filename_from_path(ui_filepath)}.py"
        return os.sep.join([self.dir_path, py_filename])


class UiEventHandler(events.FileSystemEventHandler):
    def __init__(self, dir_path: Str, pyfile_manager: UiPyManager):
        super().__init__()
        self.dir_path = dir_path
        self.pyfile_manager = pyfile_manager

    @override
    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return

        self.pyfile_manager.clear()
        for (_, _, files) in os.walk(self.dir_path):
            for file in files:
                if file.endswith(".ui"):
                    self.pyfile_manager.create(os.sep.join([self.dir_path, file]))


def main():
    logs.init()

    path = sys.argv[1] if len(sys.argv) > 1 else "."
    to_path = sys.argv[2] if len(sys.argv) > 2 else path
    logs.info(f"start watching dir: {path}, generate ui.py in {to_path}")

    observer = observers.Observer()
    observer.schedule(UiEventHandler(path, UiPyManager(to_path)), path, True)
    observer.start()
    observer.join()


if __name__ == '__main__':
    main()
