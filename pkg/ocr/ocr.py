from typing import AnyStr

from PIL import Image
import pytesseract

from pkg import conf

pytesseract.pytesseract.tesseract_cmd = conf.TESSERACT_OCR_EXEC_PATH


def read_to_text(filepath: AnyStr) -> AnyStr:
    return pytesseract.image_to_string(Image.open(filepath), lang='eng')
