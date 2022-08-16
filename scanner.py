import token
from types import List

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1

    def scan_tokens(self) -> List[token.Token]:
        while not self._is_at_end():
            self.start = self.current
            self.scan_token()

        self.tokens.append(token.Token(token.TokenType.EOF, "", None, self.line))
        return self.tokens

    def scan_token(self):
        c = self.advance()
        if c == '(':
            self.add_token(token.TokenType.LEFT_PAREN)
        elif c == ')':
            self.add_token(token.TokenType.RIGHT_PAREN)
        elif c == '{':
            self.add_token(token.TokenType.LEFT_BRACE)
        elif c == '}':
            self.add_token(token.TokenType.RIGHT_BRACE)
        elif c == ',':
            self.add_token(token.TokenType.COMMA)
        elif c == '.':
            self.add_token(token.TokenType.DOT)
        elif c == '-':
            self.add_token(token.TokenType.MINUS)
        elif c == '+':
            self.add_token(token.TokenType.PLUS)
        elif c == ';':
            self.add_token(token.TokenType.SEMICOLON)
        elif c == '*':
            self.add_token(token.TokenType.STAR)

    def _is_at_end(self):
        return self.current >= len(self.source)
    