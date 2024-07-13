from PySide6 import QtCore, QtWidgets


def abs_rect(r: QtCore.QRect, abs_r: QtCore.QRect):
    x, y, w, h = r.x(), r.y(), r.width(), r.height()
    if w < 0:
        w = -w
        x -= w
    if h < 0:
        h = -h
        y -= h
    abs_r.setRect(x, y, w, h)


def center_widget(whole_size: QtCore.QSize, widget: QtWidgets.QWidget):
    widget.setGeometry(
        int((whole_size.width() - widget.width()) / 2),
        int((whole_size.height() - widget.height()) / 2),
        widget.width(),
        widget.height()
    )
