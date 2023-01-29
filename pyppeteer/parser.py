import os
import abc

from pyppeteer.scanner import Scanner, TokenType
from pyppeteer.exceptions import ParseSyntaxException

MODULE_TOKEN_TYPES = [TokenType.MODULE_NLP,
                      TokenType.MODULE_TAB,
                      TokenType.MODULE_STD,
                      TokenType.MODULE_CONV,
                      TokenType.MODULE_ENC,
                      TokenType.MODULE_READ,
                      TokenType.MODULE_AI,
                      TokenType.MODULE_LIST,
                      TokenType.MODULE_ENUM,
                      TokenType.MODULE_STAT,
                      TokenType.MODULE_QR,
                      TokenType.MODULE_EXP,
                      TokenType.MODULE_ENCR,
                      TokenType.MODULE_WEB,
                      TokenType.MODULE_COLOR,
                      TokenType.MODULE_STREAM]


class Node(abc.ABC):
    pass


class StatementNode(Node):
    def __init__(self):
        super().__init__()
        self.node = None


class MethodCallNode(Node):
    def __init__(self):
        super().__init__()
        self.args = {
            'method': '',
            'args': []
        }


class ConcreteNode(abc.ABC):
    pass


class ShowImageNode(ConcreteNode):
    def __init__(self, image: str):
        super().__init__()
        self.image = image


class ShowTextNode(ConcreteNode):
    def __init__(self, text: str):
        super().__init__()
        self.text = text


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

        if not self._cur_token:
            return None

        t: TokenType = self._cur_token.ttype

        while t in MODULE_TOKEN_TYPES:
            statements.append(self._parse_statement())

            if self._cur_token is not None:
                t = self._cur_token.ttype
            else:
                break
        return statements

    def _parse_statement(self) -> StatementNode:
        node = StatementNode()
        node.node = self._parse_module_call()
        return node

    def _parse_module_call(self) -> MethodCallNode:
        node = MethodCallNode()
        node.args['module'] = self._cur_token.ttype.name

        if self._cur_token.ttype in MODULE_TOKEN_TYPES:
            self._accept(self._cur_token.ttype)
        else:
            self._fail('Unexpected token ' + self._cur_token)

        self._accept(TokenType.MODULE_DOT)
        node.args['method'] = self._parse_method_name()
        self._accept(TokenType.L_PAREN)
        node.args['args'] = self._parse_named_args()
        self._accept(TokenType.R_PAREN)

        return node

    def _parse_file_desc(self) -> str:
        path_str = self._cur_token.value
        if os.path.isfile(path_str):
            return path_str
        self._fail('File ' + path_str + ' not found!')

    def _parse_method_name(self) -> str:
        return_str = self._cur_token.value
        self._accept(TokenType.STRING_IDENTIFIER)
        return return_str

    def _parse_named_args(self) -> []:
        named_args_tuples = []
        while self._cur_token.ttype in [TokenType.STRING_IDENTIFIER, TokenType.CHAR_COMMA]:
            if self._cur_token.ttype == TokenType.CHAR_COMMA:
                self._accept(TokenType.CHAR_COMMA)
            key = self._cur_token.value
            self._accept(TokenType.STRING_IDENTIFIER)
            self._accept(TokenType.CHAR_EQUALS)
            value = self._cur_token.value
            self._accept(TokenType.STRING)
            named_args_tuples.append((key, value))
        return named_args_tuples

