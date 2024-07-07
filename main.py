import sys

import win32con
from PySide6 import QtWidgets
from PySide6 import QtCore

import component
import hotkey


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = component.Window()
    window.showMinimized()

    m = hotkey.HotkeyManager()
    m.register(
        hotkey.Hotkey(
            window.hotkey_signal.emit,
            hotkey.HotkeyFsModifiers.MOD_NONE,
            win32con.VK_F4,
        )
    )
    m.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
