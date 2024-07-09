import sys

import win32con
from PySide6 import QtWidgets
from PySide6 import QtCore

import component
import hotkey


def main():
    app = QtWidgets.QApplication(sys.argv)
    m = hotkey.HotkeyManager()

    window = component.Window(hk_manager=m)
    window.showMinimized()

    m.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
