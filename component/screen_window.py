from typing import override

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
            # FIXME: it will make maximum window to normal
            code = win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
            logs.info(f"show window {self.hwnd}, code is {code}")
            self.hwnd = self._EMPTY_HWND

    @QtCore.Slot(QtCore.QRect)
    def _hello(self, rect: QtCore.QRect):
        logs.info(f"clipped: {rect}")


class _ImageClipper(QtWidgets.QLabel):
    _CLIPPED_THRESHOLD = 1
    clipped = QtCore.Signal(QtCore.QRect)

    _OVERLAY_BRUSH = QtGui.QBrush(QtGui.QColor(0, 0, 0, 50))
    _EMPTY_BRUSH = QtGui.QBrush()
    _BORDER_PEN = QtGui.QPen(Qt.GlobalColor.red, 1)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.rect = QtCore.QRect()
        self._overlay_rect = QtCore.QRect()
        self._abs_rect = QtCore.QRect()

    def _draw_rect(self, painter: QtGui.QPainter, rect: QtCore.QRect):
        painter.setPen(self._BORDER_PEN)
        painter.drawRect(rect)

    def _draw_outside_overlay(self, painter: QtGui.QPainter, rect: QtCore.QRect):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self._OVERLAY_BRUSH)

        # left
        self._overlay_rect.setRect(0, 0, rect.left(), self.height())
        painter.drawRect(self._overlay_rect)
        # top
        self._overlay_rect.setRect(rect.left(), 0, self.width() - rect.left(), rect.top())
        painter.drawRect(self._overlay_rect)
        # right
        # +1 to avoid unintended problem
        self._overlay_rect.setRect(rect.right() + 1, rect.top(), self.width() - rect.width(), self.height() - rect.top())
        painter.drawRect(self._overlay_rect)
        # bottom
        self._overlay_rect.setRect(rect.left(), rect.bottom(), rect.width(), self.height() - rect.bottom())
        painter.drawRect(self._overlay_rect)

        painter.setBrush(self._EMPTY_BRUSH)

    @override
    def paintEvent(self, event):
        super().paintEvent(event)
        _convert_rect_to_abs(self.rect, self._abs_rect)

        painter = QtGui.QPainter()
        painter.begin(self)
        self._draw_outside_overlay(painter, self._abs_rect)
        self._draw_rect(painter, self._abs_rect)
        painter.end()

    @override
    def mousePressEvent(self, ev):
        self.rect = QtCore.QRect(ev.x(), ev.y(), 0, 0)

    @override
    def mouseMoveEvent(self, ev):
        start_x, start_y = self.rect.x(), self.rect.y()
        self.rect.setRect(start_x, start_y, ev.x() - start_x, ev.y() - start_y)
        self.update()

    @override
    def mouseReleaseEvent(self, ev):
        if self.rect.width() * self.rect.height() < self._CLIPPED_THRESHOLD:
            logs.info("selected area is too small, please reselect an area")
            return
        self.clipped.emit(self.rect)

    @override
    def mouseDoubleClickEvent(self, event):
        self.parent().mouseDoubleClickEvent(event)


def _convert_rect_to_abs(rect: QtCore.QRect, dest: QtCore.QRect):
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    if w < 0:
        w = -w
        x -= w
    if h < 0:
        h = -h
        y -= h
    dest.setRect(x, y, w, h)
