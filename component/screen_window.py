import win32con
import win32gui
from PySide6 import QtWidgets, QtGui, QtCore
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
            | Qt.WindowType.WindowStaysOnTopHint
        )

        layout = QtWidgets.QVBoxLayout()
        self.clipper = _ImageClipper(self)
        self.clipper.resize(self.screen().size())
        layout.addWidget(self.clipper, Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.clipper.clipped.connect(self._hello)

    def close(self):
        self._restore_foreground_window()
        super().close()

    def mouseDoubleClickEvent(self, event):
        self.close()

    def display(self, img: QtGui.QPixmap | QtGui.QImage):
        self.hwnd = win32gui.GetForegroundWindow()
        self.resize(img.size())
        self.clipper.setPixmap(img)
        self.show()

    def _restore_foreground_window(self):
        if self.hwnd != self._EMPTY_HWND:
            code = win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            logs.info(f"show window {self.hwnd}, code is {code}")
            self.hwnd = self._EMPTY_HWND

    @QtCore.Slot(QtCore.QRect)
    def _hello(self, rect: QtCore.QRect):
        logs.info(f"clipped: {rect}")


class _ImageClipper(QtWidgets.QLabel):
    _CLIPPED_THRESHOLD = 1
    clipped = QtCore.Signal(QtCore.QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rect = QtCore.QRect()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        if not self.rect.isEmpty():
            self._draw_rect(painter)
        painter.end()

    def _draw_rect(self, painter: QtGui.QPainter):
        pen = QtGui.QPen(Qt.GlobalColor.red, 1)
        painter.setPen(pen)
        painter.drawRect(self.rect)

    def mousePressEvent(self, ev):
        self.rect = QtCore.QRect(ev.x(), ev.y(), 0, 0)

    def mouseMoveEvent(self, ev):
        start_x, start_y = self.rect.x(), self.rect.y()
        self.rect.setRect(start_x, start_y, ev.x() - start_x, ev.y() - start_y)
        self.update()

    def mouseReleaseEvent(self, ev):
        if self.rect.width() * self.rect.height() < self._CLIPPED_THRESHOLD:
            return
        self.clipped.emit(self.rect)

    def mouseDoubleClickEvent(self, event):
        self.parent().mouseDoubleClickEvent(event)
