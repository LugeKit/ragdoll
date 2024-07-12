import enum
from typing import override

import win32con
import win32gui
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt

from pkg import logs, conf, fsm, ocr
from ui_py import ui_clip_toolkit


class ScreenWindow(QtWidgets.QMainWindow):
    def __init__(self, img: QtGui.QPixmap | QtGui.QImage):
        super().__init__(None)  # parent should be None to display in fullscreen
        self.img = img
        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)
        self.clipper = self._new_clipper(self.img)
        self._hwnd = win32gui.GetForegroundWindow()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.CustomizeWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.resize(self.screen().size())

        confirm_shortcut = QtGui.QShortcut(conf.KEY_CONFIRM_CLIP, self)
        confirm_shortcut.activated.connect(self._confirm)
        cancel_shortcut = QtGui.QShortcut(conf.KEY_CANCEL_CLIP, self)
        cancel_shortcut.activated.connect(self._cancel)

        self.show()

    def _confirm(self):
        self.clipper.confirm_sig.emit()

    def _cancel(self):
        if self.clipper.state() == _ImageClipper.State.Empty:
            self.close()
            return

        self.clipper.cancel_sig.emit()

    def close(self):
        self._restore_foreground_window()
        self.layout().removeWidget(self.clipper)
        self.clipper = None
        super().close()

    def mouseDoubleClickEvent(self, event):
        self.close()

    def _new_clipper(self, img: QtGui.QPixmap | QtGui.QImage):
        clipper = _ImageClipper(self)
        clipper.resize(self.screen().size())
        clipper.setPixmap(img)
        clipper.clipped_sig.connect(self._on_clipped_success)
        self.layout().addWidget(clipper)
        return clipper

    def _restore_foreground_window(self):
        # FIXME: it will make maximum window to normal
        code = win32gui.ShowWindow(self._hwnd, win32con.SW_RESTORE)
        logs.info(f"show window {self._hwnd}, code is {code}")

    @QtCore.Slot(QtCore.QRect)
    def _on_clipped_success(self, rect: QtCore.QRect):
        if not self.img:
            logs.error("self.img is None")
            self.close()
            return

        clipped_pixmap = self.img.copy(self._scale_rect_by_size(rect))
        if clipped_pixmap.save("tmp/tmp.png"):
            logs.info(f"ocr result is: {ocr.read_to_text('tmp/tmp.png')}")
        self.close()

    def _scale_rect_by_size(self, rect: QtCore.QRect) -> QtCore.QRect:
        img_size = self.img.size()
        clipper_size = self.clipper.size()

        if clipper_size.width() == 0 or clipper_size.height() == 0:
            raise RuntimeError("clipper size is abnormal")

        x_scale = img_size.width() / clipper_size.width()
        y_scale = img_size.height() / clipper_size.height()

        logs.debug(f"rect before resize: {rect}")
        rect.setRect(
            int(rect.x() * x_scale),
            int(rect.y() * y_scale),
            int(rect.width() * x_scale),
            int(rect.height() * y_scale),
        )
        logs.debug(f"rect after resize: {rect}")
        return rect


class _ImageClipper(QtWidgets.QLabel):
    _CLIPPED_THRESHOLD = 1
    clipped_sig = QtCore.Signal(QtCore.QRect)
    confirm_sig = QtCore.Signal()
    cancel_sig = QtCore.Signal()

    _OVERLAY_BRUSH = QtGui.QBrush(QtGui.QColor(0, 0, 0, 50))
    _EMPTY_BRUSH = QtGui.QBrush()
    _BORDER_WIDTH = 1
    _BORDER_PEN = QtGui.QPen(Qt.GlobalColor.red, _BORDER_WIDTH)

    class State(enum.StrEnum):
        Empty = "empty",
        Clipping = "clipping",
        Clipped = "clipped"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._toolkit = _ClipToolkit(self)
        self._toolkit.hide()
        self._toolkit.cancel_sig.connect(self.cancel_sig)
        self._toolkit.confirm_sig.connect(self.confirm_sig)

        self._rect = QtCore.QRect()
        self._overlay_rect = QtCore.QRect()
        self._abs_rect = QtCore.QRect()

        self.confirm_sig.connect(self._confirm)
        self.cancel_sig.connect(self._cancel)

        self._state_machine = fsm.Machine(
            {
                fsm.State(
                    name=self.State.Empty,
                    next_states={"clipping"},
                ),
                fsm.State(
                    name=self.State.Clipping,
                    next_states={"empty", "clipped"},
                ),
                fsm.State(
                    name=self.State.Clipped,
                    next_states={"empty", "clipping"},
                    on_enter=self._on_enter_clipped,
                    on_exit=self._on_exit_clipped,
                ),
            },
            self.State.Empty
        )

    def state(self):
        return self._state_machine.state()

    def _on_enter_clipped(self, from_state: fsm.Str):
        _convert_rect_to_abs(self._rect, self._abs_rect)
        self._toolkit.setGeometry(self._abs_rect.right() - self._toolkit.width() + self._BORDER_WIDTH,
                                  self._abs_rect.bottom(),
                                  self._toolkit.width(),
                                  self._toolkit.height())
        self._toolkit.show()

    def _on_exit_clipped(self, to_state: fsm.Str):
        self._toolkit.hide()

    def _cancel(self):
        logs.debug(f"_cancel is called, current state is {self.state()}")
        self._reset()

    def _confirm(self):
        logs.debug(f"_confirm is called, current state is {self.state()}")
        if self.state() in {"clipping", "clipped"}:
            if self._clip_area() < self._CLIPPED_THRESHOLD:
                logs.info(f"selected area {self._abs_rect} is too small, please reselect an area")
                return
            self._reset()
            self.clipped_sig.emit(QtCore.QRect(self._abs_rect))

    @override
    def mousePressEvent(self, ev):
        logs.debug("mouse is pressed")
        self._reset()
        try:
            self._state_machine.trans_to("clipping")
            self._rect.setRect(ev.x(), ev.y(), 0, 0)
        except (fsm.StateNotFound, fsm.StateTransIllegal) as e:
            logs.error(e)

    @override
    def mouseMoveEvent(self, ev):
        logs.debug("mouse is moving")
        if self.state() != "clipping":
            try:
                self._state_machine.trans_to("clipping")
                self._rect.setRect(ev.x(), ev.y(), 0, 0)
            except (fsm.StateNotFound, fsm.StateTransIllegal) as e:
                logs.error(e)
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

        try:
            self._state_machine.trans_to("clipped")
        except (fsm.StateNotFound, fsm.StateTransIllegal) as e:
            logs.error(e)

    def _reset(self):
        try:
            self._state_machine.trans_to("empty")
            self._rect.setRect(0, 0, 0, 0)
            self.update()
        except (fsm.StateNotFound, fsm.StateTransIllegal) as e:
            logs.error(e)

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


class _ClipToolkit(QtWidgets.QWidget, ui_clip_toolkit.Ui_Form):
    cancel_sig = QtCore.Signal()
    confirm_sig = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.cancel_btn.clicked.connect(self.cancel_sig)
        self.confirm_btn.clicked.connect(self.confirm_sig)
