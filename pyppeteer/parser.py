import os
import abc
from pyppeteer.scanner import Scanner, TokenType, Token
from pyppeteer.exceptions import ParseSyntaxException


class Node(abc.ABC):
    pass


class StatementNode(Node):
    def __init__(self):
        super().__init__()
        self.node = None
        self.time_mark: int = 0


class ShowNode(Node):
    def __init__(self):
        super().__init__()
        self.args = {
            'file': ''
        }


class Parser:
    def __init__(self):
        self._scanner = Scanner()
        self._cur_token = None
        self._prev_token = None
        self._statements: [StatementNode] = []

    def _next_token(self, peek: bool = False):
        if self._cur_token is not None:
            self._prev_token = self._cur_token
        return self._scanner.next_token(peek)

    @staticmethod
    def _clean_string(s: str):
        lines = list(filter(lambda e: len(e), [ln.lstrip() for ln in s.splitlines()]))
        for ln, _ in enumerate(lines):
            lines[ln] = ''.join(lines[ln])
        return '\n'.join(lines) + '\n'

    def parse(self, input_str: str) -> [StatementNode]:
        # Parse given input string
        # We perform some string cleaning and whitespace removing before actually passing the raw string to the scanner
        clean_str = self._clean_string(input_str)

        self._scanner = Scanner()
        self._prev_token = None
        self._statements = []
        self._scanner.scan_str(clean_str)
        self._cur_token = self._next_token()
        return self._parse_statements()

    def _accept(self, ttype: TokenType):
        if self._cur_token is not None:
            if self._cur_token.ttype == ttype:
                self._cur_token = self._next_token()
            else:
                self._fail(msg="Expected {e}, got {t}".format(e=ttype, t=self._cur_token))
        else:
            self._fail(msg="Unexpected EOF")

    def _fail(self, msg: str = ''):
        try:
            char_offset = self._cur_token.meta_cn
        except AttributeError:
            char_offset = self._scanner.char_offset
        raise ParseSyntaxException('PARSER ERROR,{msg},{cn}'.format(msg=msg, cn=char_offset))

    def _cur_token_type(self):
        if self._cur_token is not None:
            return self._cur_token.ttype
        else:
            return TokenType.EOF

    def _parse_statements(self) -> [StatementNode]:
        statements = []
        t: TokenType = self._cur_token.ttype

        while t in [TokenType.NUMBER]:
            if t == TokenType.NUMBER:
                statements.append(self._parse_statement())
            # elif t == TokenType.BLOCK_IF:
            #     statements.append(self._parse_if())
            # elif t == TokenType.LOOP_REPEAT:
            #     statements.append(self._parse_loop())
            # elif t == TokenType.LOOP_FOR:
            #     statements.append(self._parse_for_loop())
            # elif t == TokenType.LOOP_BREAK:
            #     statements.append(self._parse_exit())
            # elif t == TokenType.IDENTIFIER:
            #     if self._next_token(peek=True).ttype == TokenType.LPARENT:
            #         statements.append(self._parse_call())
            #     else:
            #         statements.append(self._parse_lmodify())
            # elif t == TokenType.PROC_SUB:
            #     statements.append(self._parse_sub())
            # elif t == TokenType.PROC_RETURN:
            #     statements.append(self._parse_subreturn())
            # elif t == TokenType.PROC_FUNC:
            #     statements.append(self._parse_func())
            # elif t == TokenType.API_EXTERN:
            #     statements.append(self._parse_extern())

            if self._cur_token is not None:
                t = self._cur_token.ttype
            else:
                break
        return statements

    def _parse_statement(self) -> StatementNode:
        node = StatementNode()
        node.time_mark = self._cur_token.value
        self._accept(TokenType.NUMBER)
        self._accept(TokenType.CHAR_COLON)

        if self._cur_token.ttype == TokenType.SHOW:
            node.node = self._parse_show()
        else:
            pass
            # let my_var = (3 + 42)
            # node.right = self._parse_expression()

        return node

    def _parse_show(self) -> ShowNode:
        node = ShowNode()

        self._accept(TokenType.SHOW)
        if self._cur_token.ttype in [TokenType.SHOW_TEXT, TokenType.SHOW_LINE, TokenType.SHOW_RECT,
                                     TokenType.SHOW_IMAGE, TokenType.SHOW_ELLIPSOID, TokenType.SHOW_CIRCLE]:
            self._accept(self._cur_token.ttype)
        else:
            self._fail('Unexpected token ' + self._cur_token)

        node.args['file'] = self._parse_file_desc()
        self._accept(TokenType.STRING)

        # Optional: for number interval (e.g., for 5s)
        if self._cur_token and self._cur_token.ttype == TokenType.FOR:
            self._accept(TokenType.FOR)
            node.args['duration'] = self._parse_duration()

        return node

    def _parse_file_desc(self) -> str:
        path_str = self._cur_token.value
        if os.path.isfile(path_str):
            return path_str
        self._fail('File ' + path_str + ' not found!')

    def _parse_duration(self) -> int:
        # number (ms|s|m)
        unit = self._cur_token.value
        quantity = unit.quantity

        if unit.unit == 's':
            factor = 1
        elif unit.unit == 'ms':
            factor = .001
        elif unit.unit == 'm':
            factor = 60
        else:
            self._fail('Unknown time unit for duration')

        self._accept(TokenType.UNIT)
        return quantity * factor

