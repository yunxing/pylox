from tokens import Token
import lox_ast
from typing import List, Any
import dataclasses


@dataclasses.dataclass
class ParserErrorFrame:
    token: Token
    message: str

    def __str__(self):
        return f"{self.token.line} - {self.token}: {self.message}"

# Define an exception class for our parser error.


class ParserError(Exception):
    def __init__(self, token: Token, message: str):
        self.token = token
        self.message = message

    def __str__(self):
        return f"{self.token.line} - {self.token}: {self.message}"


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0
        self.errors: List[ParserErrorFrame] = []

    def parse(self, tokens: List[Token]) -> lox_ast.Expr:
        self.tokens = tokens
        self.current = 0
        self.errors: List[ParserErrorFrame] = []

        try:
            return self.expression()
        except ParserError as e:
            print(e)
            return None

    def add_error(self, message: str):
        self.errors.append(ParserErrorFrame(self.peek(), message))

    def expression(self) -> lox_ast.Expr:
        return self.equality()

    def left_associative_binary(self, parse_right, match_tokens: List[Token.TokenType]) -> lox_ast.Expr:
        '''
        Helper function for binary expressions that are left associative.
        '''
        expr = parse_right()

        while self.match(*match_tokens):
            operator = self.previous()
            right = parse_right()
            expr = lox_ast.Binary(expr, operator, right)

        return expr

    def equality(self) -> lox_ast.Expr:
        return self.left_associative_binary(self.comparison, [Token.TokenType.BANG_EQUAL, Token.TokenType.EQUAL_EQUAL])

    def comparison(self) -> lox_ast.Expr:
        return self.left_associative_binary(self.term, [Token.TokenType.GREATER, Token.TokenType.GREATER_EQUAL, Token.TokenType.LESS, Token.TokenType.LESS_EQUAL])

    def term(self) -> lox_ast.Expr:
        return self.left_associative_binary(self.factor, [Token.TokenType.MINUS, Token.TokenType.PLUS])

    def factor(self) -> lox_ast.Expr:
        return self.left_associative_binary(self.unary, [Token.TokenType.SLASH, Token.TokenType.STAR])

    def unary(self) -> lox_ast.Expr:
        if self.match(Token.TokenType.BANG, Token.TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return lox_ast.Unary(operator, right)
        return self.primary()

    def primary(self) -> lox_ast.Expr:
        if self.match(Token.TokenType.FALSE):
            return lox_ast.Literal(False)
        if self.match(Token.TokenType.TRUE):
            return lox_ast.Literal(True)
        if self.match(Token.TokenType.NIL):
            return lox_ast.Literal(None)
        if self.match(Token.TokenType.NUMBER, Token.TokenType.STRING):
            return lox_ast.Literal(self.previous().literal)
        if self.match(Token.TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(Token.TokenType.RIGHT_PAREN,
                         "Expect ')' after expression.")
            return lox_ast.Grouping(expr)
        self.error(self.peek(), "Expect expression.")

    def consume(self, token_type: Token.TokenType, message: str):
        if self.check(token_type):
            return self.advance()
        self.error(self.peek(), message)

    def error(self, token: Token, message: str):
        self.add_error(message)
        raise ParserError(token, message)

    def synchronize(self):
        '''
        Advance the parser until it finds a token that can be used to continue parsing.
        '''
        self.advance()

        while not self.is_at_end():
            if self.previous().token_type == Token.TokenType.SEMICOLON:
                return

            token_type = self.peek().token_type
            if token_type in [Token.TokenType.CLASS, Token.TokenType.FUN, Token.TokenType.VAR, Token.TokenType.FOR, Token.TokenType.IF, Token.TokenType.WHILE, Token.TokenType.PRINT, Token.TokenType.RETURN]:
                return

            self.advance()

    def match(self, *token_types: Token.TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type: Token.TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().token_type == token_type

    def is_at_end(self):
        return self.peek().token_type == Token.TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        assert self.current > 0
        return self.tokens[self.current - 1]
