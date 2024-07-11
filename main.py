import sys

from PySide6 import QtWidgets

import component
from pkg import logs, hotkey


def main():
    logs.init()
    logs.info("start process")

    app = QtWidgets.QApplication(sys.argv)
    m = hotkey.HotkeyManager()

    window = component.Window(hk_manager=m)
    window.showMinimized()

    m.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
