import enum
from typing import override

import win32con
import win32gui
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt

import conf
from pkg import logs


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

        self.clipper.clipped_sig.connect(self._hello)

        confirm_shortcut = QtGui.QShortcut(conf.KEY_CONFIRM_CLIP, self)
        confirm_shortcut.activated.connect(self._confirm)
        cancel_shortcut = QtGui.QShortcut(conf.KEY_CANCEL_CLIP, self)
        cancel_shortcut.activated.connect(self._cancel)

    def _confirm(self):
        self.clipper.confirm_sig.emit()

    def _cancel(self):
        if self.clipper.state == _ImageClipper.State.EMPTY:
            self.close()
            return

        self.clipper.cancel_sig.emit()

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
        self.close()


class _ImageClipper(QtWidgets.QLabel):
    _CLIPPED_THRESHOLD = 1
    clipped_sig = QtCore.Signal(QtCore.QRect)
    confirm_sig = QtCore.Signal()
    cancel_sig = QtCore.Signal()

    _OVERLAY_BRUSH = QtGui.QBrush(QtGui.QColor(0, 0, 0, 50))
    _EMPTY_BRUSH = QtGui.QBrush()
    _BORDER_PEN = QtGui.QPen(Qt.GlobalColor.red, 1)

    class State(enum.StrEnum):
        EMPTY = "EMPTY"
        CLIPPING = "CLIPPING"
        CLIPPED = "CLIPPED"

    def __init__(self, parent=None):
        super().__init__(parent)

        self.state = self.State.EMPTY

        self._rect = QtCore.QRect()
        self._overlay_rect = QtCore.QRect()
        self._abs_rect = QtCore.QRect()

        self.confirm_sig.connect(self._confirm)
        self.cancel_sig.connect(self._cancel)

    def _cancel(self):
        logs.debug(f"_cancel is called, current state is {self.state}")
        self._reset()

    def _confirm(self):
        logs.debug(f"_confirm is called, current state is {self.state}")
        if self.state in {self.State.CLIPPING, self.state.CLIPPED}:
            if self._clip_area() < self._CLIPPED_THRESHOLD:
                logs.info(f"selected area {self._abs_rect} is too small, please reselect an area")
                return
            self._reset()
            self.clipped_sig.emit(QtCore.QRect(self._abs_rect))

    @override
    def mousePressEvent(self, ev):
        self.state = self.state.CLIPPING
        self._rect.setRect(ev.x(), ev.y(), 0, 0)

    @override
    def mouseMoveEvent(self, ev):
        if self.state in {self.State.EMPTY, self.state.CLIPPED}:
            self.state = self.state.CLIPPING
            self._rect.setRect(ev.x(), ev.y(), 0, 0)
            return

        start_x, start_y = self._rect.x(), self._rect.y()
        self._rect.setRect(start_x, start_y, ev.x() - start_x, ev.y() - start_y)
        self.update()

    @override
    def mouseReleaseEvent(self, ev):
        logs.debug("mouse is released")
        if self._clip_area() < self._CLIPPED_THRESHOLD:
            logs.info(f"selected area {self._abs_rect} is too small, reset to zero")
            self._reset()
            return

        self.state = self.State.CLIPPED

    def _reset(self):
        self.state = self.state.EMPTY
        self._rect.setRect(0, 0, 0, 0)
        self.update()

    def _clip_area(self) -> int:
        _convert_rect_to_abs(self._rect, self._abs_rect)
        return self._abs_rect.width() * self._abs_rect.height()

    @override
    def paintEvent(self, event):
        super().paintEvent(event)
        _convert_rect_to_abs(self._rect, self._abs_rect)

        painter = QtGui.QPainter()
        painter.begin(self)
        self._draw_outside_overlay(painter, self._abs_rect)
        self._draw_rect(painter, self._abs_rect)
        painter.end()

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


def _convert_rect_to_abs(rect: QtCore.QRect, dest: QtCore.QRect):
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    if w < 0:
        w = -w
        x -= w
    if h < 0:
        h = -h
        y -= h
    dest.setRect(x, y, w, h)
