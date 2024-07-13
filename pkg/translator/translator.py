from typing import AnyStr, LiteralString, override

import translate as tr

from pkg import conf


class Translator:
    def __init__(self):
        pass

    def translate(self, text: AnyStr | LiteralString) -> str:
        return ""


class DefaultTranslator(Translator):
    def __init__(self):
        super().__init__()

    @override
    def translate(self, text: AnyStr | LiteralString) -> str:
        return ""


_translator = tr.Translator(to_lang=conf.ocr.to_lang)


def init():
    pass


def translate(text: AnyStr | LiteralString) -> str:
    return _translator.translate(text)
