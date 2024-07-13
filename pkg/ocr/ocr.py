import io
from typing import AnyStr

import pytesseract
from PIL import Image
from PySide6 import QtGui, QtCore

from pkg import conf

pytesseract.pytesseract.tesseract_cmd = conf.TESSERACT_OCR_EXEC_PATH


def from_file(filepath: AnyStr) -> AnyStr:
    return pytesseract.image_to_string(Image.open(filepath), lang='eng')


def from_qpixmap(image: QtGui.QPixmap) -> AnyStr:
    buffer = QtCore.QBuffer()
    buffer.open(QtCore.QIODeviceBase.OpenModeFlag.ReadWrite)
    image.save(buffer, "PNG")
    return pytesseract.image_to_string(
        Image.open(io.BytesIO(buffer.data().data())),
        lang='eng'
    )
