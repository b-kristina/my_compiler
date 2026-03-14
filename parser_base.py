from contextlib import suppress
from typing import Union

class ParsingError(Exception):
    """Класс для исключений парсинга"""
    def __init__(self, message):
        super().__init__(message)

class BaseParser:
    """Базовый класс для построения парсеров"""
    def __init__(self, text: str):
        """
        Конструктор
        :param text: текст программы
        """
        self.text = text
        self.pos = 0

    @property
    def curr(self) -> str:
        """Возвращает текущий символ"""
        return self.text[self.pos] if self.pos < len(self.text) else '$'

    def ws(self):
        """Пропускает пробельные символы"""
        while self.curr.isspace():
            self.pos += 1

    def parse(self, s1: str, *s: str) -> Union[str, None]:
        """
        Ищет в текущей позиции и возвращает первое совпадение из (s1, *s)
        Указатель смещается
        :param (s1, *s) - допустимые фрагменты
        :exception ParsingError
        """
        self.ws()
        for ss in (s1, *s):
            if self.text[self.pos:self.pos + len(ss)] == ss:
                self.pos += len(ss)
                self.ws()
                return ss
        raise ParsingError(f'Ни один фрагмент из {(s1, *s)} не найден!')

    def is_parse(self, s1: str, *s: str) -> Union[str, None]:
        """
        Ищет в текущей позиции и возвращает первое совпадение из (s1, *s)
        Указатель не смещается
        :param (s1, *s) - допустимые фрагменты
        """
        pos = self.pos
        res = None
        with suppress(ParsingError):
            res = self.parse(s1, *s)
        self.pos = pos
        return res