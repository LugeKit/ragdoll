import sys

from PySide6 import QtWidgets

import component


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = component.Window()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
