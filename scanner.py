import tokens
from typing import List, Any
import dataclasses


@dataclasses.dataclass
class ErrorFrame:
    line: int
    message: str

    def __str__(self):
        return f"{self.line}: {self.message}"


class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.error_frames = []

    def scan_tokens(self) -> List[tokens.Token]:
        while not self._is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(tokens.Token(
            tokens.TokenType.EOF, "", None, self.line))
        return self.tokens

    def add_error(self, message: str):
        self.error_frames.append(ErrorFrame(self.line, message))

    def scan_token(self):
        c = self._advance()
        if c == '(':
            self.add_token(tokens.TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(tokens.TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(tokens.TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(tokens.TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(tokens.TokenType.COMMA)
        elif c == '.':
            self.add_token(tokens.TokenType.DOT)
        elif c == '-':
            self.add_token(tokens.TokenType.MINUS)
        elif c == '+':
            self.add_token(tokens.TokenType.PLUS)
        elif c == ';':
            self.add_token(tokens.TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(tokens.TokenType.STAR)
        elif c == '!':
            if self.match('='):
                self.add_token(tokens.TokenType.BANG_EQUAL)
            else:
                self.add_token(tokens.TokenType.BANG)
        elif c == '=':
            if self.match('='):
                self.add_token(tokens.TokenType.EQUAL_EQUAL)
            else:
                self.add_token(tokens.TokenType.EQUAL)
        elif c == '<':
            if self.match('='):
                self.add_token(tokens.TokenType.LESS_EQUAL)
            else:
                self.add_token(tokens.TokenType.LESS)
        elif c == '>':
            if self.match('='):
                self.add_token(tokens.TokenType.GREATER_EQUAL)
            else:
                self.add_token(tokens.TokenType.GREATER)
        elif c == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self._is_at_end():
                    self._advance()
            else:
                self.add_token(tokens.TokenType.SLASH)
        elif c == ' ' or c == '\r' or c == '\t':
            pass
        elif c == '\n':
            self.line += 1
        elif c == '"':
            self.string()
        # check if c is a number
        elif c.isdigit():
            self._number()
        # check if c is a letter
        elif c.isalpha() or c == '_':
            self._identifier()
        else:
            self.add_error(f"Unexpected character {c}")

    def _identifier(self):
        while self.peek().isalpha() or self.peek().isdigit() or self.peek() == '_':
            self._advance()
        text = self.source[self.start:self.current]
        if tokens.is_reserved_keyword(text):
            self._add_token(tokens.get_reserved_keyword_as_token(text))
            return
        self._add_token(tokens.TokenType.IDENTIFIER, text)

    def _number(self):
        while self.peek().isdigit():
            self._advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()

            while self.peek().isdigit():
                self.advance()

        self._add_token(tokens.TokenType.NUMBER, float(
            self.source[self.start:self.current]))

    def string(self):
        while self.peek() != '"' and not self._is_at_end():
            if self.peek() == '\n':
                self.line += 1
            self.advance()

        if self._is_at_end():
            self.add_error("Unterminated string")
            return
        self.advance()
        value = self.source[self.start + 1:self.current - 1]
        self._add_token(tokens.TokenType.STRING, value)

    def peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self. current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        self.current += 1
        return True

    def _advance(self) -> str:
        r = self.source[self.current]
        self.current += 1
        return r

    def _add_token(self, token_type: tokens.TokenType, literal: Any = None):
        text = self.source[self.start:self.current]
        self.tokens.append(tokens.Token(token_type, text, literal, self.line))

    def _is_at_end(self):
        return self.current >= len(self.source)
