from __future__ import annotations

import enum
from typing import Optional
from pyppeteer.exceptions import ScanWrongTokenException


class TokenType(enum.Enum):
    NUMBER = 1
    STRING = 2
    REFERENCE = 3

    CHAR_COLON = 20
    CHAR_COMMA = 21
    CHAR_AT = 22
    CHAR_HASH = 23

    TRANSITION_DEFINE = 30
    TRANSITION_TRANSITION = 31
    TRANSITION_SLIDE_LEFT = 32
    TRANSITION_SLIDE_RIGHT = 33
    TRANSITION_SLIDE_TOP = 34
    TRANSITION_SLIDE_BOTTOM = 35
    TRANSITION_FADE_IN = 36
    TRANSITION_FADE_OUT = 37
    TRANSITION_WITH = 38
    TRANSITION_DURATION = 39

    REFERENCE_AS = 40

    SHOW = 60
    SHOW_IMAGE = 61
    SHOW_TEXT = 62
    SHOW_CIRCLE = 63
    SHOW_RECT = 64
    SHOW_ELLIPSOID = 65
    SHOW_LINE = 66
    SHOW_HIDE = 67

    PLAY = 60
    PLAY_SOUND = 61

    AT = 80
    FOR = 81
    AFTER = 82
    UNIT = 83

    EOF = 999


class Unit:
    def __init__(self, quantity: float, unit: str):
        self.quantity = quantity
        self.unit = unit


class Token(object):
    def __init__(self, ttype: TokenType, cn: int, value=None):
        self.ttype = ttype
        self.value = value
        self.meta_cn = cn  # Character number (for better error printing)

    def __str__(self):
        return 'Token of type {t} with value {v}'.format(t=self.ttype, v=self.value)

    def __repr__(self):
        return self.__str__()


class Scanner:
    """
    Tokenizer
    """

    def __init__(self):
        self._str_stream: str = ''
        self._char_offset: int = 0
        self._cur_char: str = ''
        self._str_len: int = 0
        self._opening_str: bool = False

    def scan_str(self, input_str: str) -> None:
        """
        Tokenize given input stream of type str
        :param input_str: Stream
        """
        self._str_stream = input_str
        self._str_len = len(self._str_stream)
        self._char_offset = 0
        self._cur_char = self._str_stream[self._char_offset]

    def next_token(self, peek: bool = False) -> Optional[Token]:
        """
        Get next available token
        :return: Token instance
        """
        while self._cur_char is not None:
            if self._cur_char.isspace():
                self._skip_whitespace()
                if self._cur_char is None:
                    return

            if self._cur_char == '#':
                # Skip comments
                while self._cur_char not in [None, '\n']:
                    self._advance(peek)
                self._advance()
                continue

            if self._cur_char == ':':
                # Define
                self._advance(peek)
                return Token(TokenType.CHAR_COLON, cn=self._char_offset)

            if self._cur_char == '@':
                # Reference
                self._advance(peek)
                return self._scan_identifier()

            if self._cur_char == ',':
                # List of coordinates
                self._advance(peek)
                return Token(TokenType.CHAR_COMMA, cn=self._char_offset)

            if self._cur_char.isdigit() or self._cur_char == '.':
                tmp_value = self._scan_number_or_duration()
                if type(tmp_value) == float:
                    return Token(TokenType.NUMBER, cn=self._char_offset, value=tmp_value)
                else:
                    return Token(TokenType.UNIT, cn=self._char_offset, value=tmp_value)

            if self._cur_char in ['"', '\'']:
                if self._opening_str:
                    raise ScanWrongTokenException('Missing closing quotes')
                return Token(TokenType.STRING, cn=self._char_offset, value=self._scan_string())

            if self._cur_char.isalpha() or self._cur_char == '_':
                return self._scan_keyword()

            raise ScanWrongTokenException('Wrong character {c} at {o}'.format(c=self._cur_char, o=self._char_offset))

    def _advance(self, peek: bool = False) -> None:
        if peek:
            return
        if self._char_offset + 1 < self._str_len:
            self._char_offset += 1
            self._cur_char = self._str_stream[self._char_offset]
        else:
            self._scan_complete()

    def _peek(self, off: int = 0) -> Optional[str]:
        if self._char_offset < self._str_len:
            return self._str_stream[self._char_offset + off]
        else:
            return None

    def _scan_complete(self) -> None:
        self._cur_char = None

    def _skip_whitespace(self) -> None:
        while self._cur_char is not None and self._cur_char.isspace():
            self._advance()

    def _scan_number_or_duration(self) -> [float | Unit]:
        tmp_num = ''
        off = 0
        scan_float = False
        scan_hex = False
        scan_unit = False
        unit = ''
        number: float
        while self._cur_char is not None and (
                self._cur_char.isalpha() or self._cur_char.isdigit() or self._cur_char in ['.', 'x']):
            if off == 0:
                if self._cur_char == '0' and self._peek(1).lower() == 'x':
                    self._advance()
                    self._advance()
                    scan_hex = True
                    scan_float = False

            if off > 0 and self._cur_char in ['s', 'm']:
                if scan_unit:
                    if unit != 'm':
                        raise ScanWrongTokenException('Invalid token for duration')
                unit += self._cur_char
                self._advance()
                scan_unit = True

            if self._cur_char == '.':
                # Leading dot without digit (.3)
                if not scan_float:
                    self._advance()
                    tmp_num += '.'
                    scan_float = True
                else:
                    raise ScanWrongTokenException()

            if self._cur_char.isdigit() or (scan_hex and self._cur_char.upper() in ['A', 'B', 'C', 'D', 'E', 'F']):
                tmp_num += self._cur_char
            # else:
            #     raise ScanWrongTokenException('Illegal number at {o}'.format(o=self._char_offset))
                self._advance()
                off += 1

        if scan_hex:
            number = float(int('0x' + tmp_num, 16))
        else:
            number = float(tmp_num)

        if scan_unit:
            return Unit(quantity=number, unit=unit)
        return number

    def _scan_string(self) -> str:
        self._opening_str = True
        tmp_str = ''
        self._advance()
        while self._cur_char is not None and self._cur_char not in ['"', '\'']:
            tmp_str += self._cur_char
            self._advance()

        if self._cur_char in ['"', '\'']:
            self._advance()
            self._opening_str = False
            return tmp_str
        else:
            raise ScanWrongTokenException()

    def _scan_identifier(self) -> Token:
        tmp_str = ''
        while self._cur_char is not None and (
                self._cur_char.isalpha() or self._cur_char.isdigit() or self._cur_char == '_'):
            tmp_str += self._cur_char
            self._advance()
        return Token(TokenType.REFERENCE, cn=self._char_offset, value=tmp_str)

    def _scan_keyword(self) -> Token:
        off = 0
        tmp_str = ''
        while self._cur_char is not None and (
                self._cur_char.isalpha() or self._cur_char.isdigit() or self._cur_char == '_'):
            if self._cur_char.isdigit() and off == 0:
                raise ScanWrongTokenException('Identifiers must not start with a digit')
            tmp_str += self._cur_char
            self._advance()
            off += 1

        slen = len(tmp_str)
        if slen == 2:
            if tmp_str == 'at':
                return Token(TokenType.AT, cn=self._char_offset)
            elif tmp_str == 'as':
                return Token(TokenType.REFERENCE_AS, cn=self._char_offset)
        elif slen == 3:
            if tmp_str == 'for':
                return Token(TokenType.FOR, cn=self._char_offset)
        elif slen == 4:
            if tmp_str == 'show':
                return Token(TokenType.SHOW, cn=self._char_offset)
            elif tmp_str == 'text':
                return Token(TokenType.SHOW_TEXT, cn=self._char_offset)
            elif tmp_str == 'rect':
                return Token(TokenType.SHOW_RECT, cn=self._char_offset)
            elif tmp_str == 'line':
                return Token(TokenType.SHOW_LINE, cn=self._char_offset)
            elif tmp_str == 'hide':
                return Token(TokenType.SHOW_HIDE, cn=self._char_offset)
            elif tmp_str == 'with':
                return Token(TokenType.TRANSITION_WITH, cn=self._char_offset)
            elif tmp_str == 'play':
                return Token(TokenType.PLAY, cn=self._char_offset)
        elif slen == 5:
            if tmp_str == 'after':
                return Token(TokenType.AFTER, cn=self._char_offset)
            elif tmp_str == 'sound':
                return Token(TokenType.PLAY_SOUND, cn=self._char_offset)
            elif tmp_str == 'image':
                return Token(TokenType.SHOW_IMAGE, cn=self._char_offset)
        elif slen == 6:
            if tmp_str == 'circle':
                return Token(TokenType.SHOW_CIRCLE, cn=self._char_offset)
        elif slen == 8:
            if tmp_str == 'duration':
                return Token(TokenType.TRANSITION_DURATION, cn=self._char_offset)
        elif slen == 9:
            if tmp_str == 'ellipsoid':
                return Token(TokenType.SHOW_ELLIPSOID, cn=self._char_offset)
        elif slen == 10:
            if tmp_str == 'transition':
                return Token(TokenType.TRANSITION_DEFINE, cn=self._char_offset)

        raise ScanWrongTokenException('Unknown token ' + tmp_str)

    @property
    def char_offset(self):
        return self._char_offset
