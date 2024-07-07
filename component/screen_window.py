import win32con
import win32gui
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt

import logs


class ScreenWindow(QtWidgets.QMainWindow):
    _EMPTY_HWND = -1

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hwnd = self._EMPTY_HWND
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.BypassWindowManagerHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        layout = QtWidgets.QVBoxLayout()

        self.label = QtWidgets.QLabel(self)
        self.label.resize(self.screen().size())
        layout.addWidget(self.label, Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def close(self):
        self._restore_foreground_window()
        super().close()

    def mouseDoubleClickEvent(self, event):
        self.close()

    def display(self, img: QtGui.QPixmap | QtGui.QImage):
        self.hwnd = win32gui.GetForegroundWindow()
        self.label.setPixmap(img)
        self.resize(img.size())
        self.show()

    def _restore_foreground_window(self):
        if self.hwnd != self._EMPTY_HWND:
            code = win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            logs.info(f"show window {self.hwnd}, code is {code}")
            self.hwnd = self._EMPTY_HWND
