from PySide6 import QtCore


def abs_rect(r: QtCore.QRect, abs_r: QtCore.QRect):
    x, y, w, h = r.x(), r.y(), r.width(), r.height()
    if w < 0:
        w = -w
        x -= w
    if h < 0:
        h = -h
        y -= h
    abs_r.setRect(x, y, w, h)
