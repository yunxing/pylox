from tokens import Token, TokenType
import expressions
import statements
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
    def __init__(self):
        self.tokens = []
        self.current = 0
        self.error_frames: List[ParserErrorFrame] = []

    def parse(self, tokens: List[Token]) -> List[statements.Stmt]:
        self.tokens = tokens
        self.current = 0
        self.error_frames: List[ParserErrorFrame] = []
        statements: List[statements.Stmt] = []

        try:
            while not self.is_at_end():
                statements.append(self.declaration())
            return statements
        except ParserError as e:
            return []

    def add_error(self, message: str):
        self.error_frames.append(ParserErrorFrame(self.peek(), message))

    def declaration(self) -> statements.Stmt:
        try:
            if self.match(TokenType.VAR):
                return self.var_declaration()
            return self.statement()
        except ParserError as e:
            self.synchronize()
            return None

    def var_declaration(self) -> statements.Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON,
                     "Expect ';' after variable declaration.")
        return statements.Var(name, initializer)

    def statement(self) -> statements.Stmt:
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.LEFT_BRACE):
            statement_list = self.block()
            self.consume(TokenType.RIGHT_BRACE,
                         "Expect ';' after return statement.")
            return statements.Block(statement_list)
        return self.expression_statement()

    def block(self) -> List[statements.Stmt]:
        statements: List[statements.Stmt] = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def for_statement(self) -> statements.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.var_declaration()
        else:
            initializer = self.expression_statement()
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        else:
            condition = expressions.Literal(True)
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        body = self.statement()
        if increment is not None:
            body = statements.Block([body, statements.Expression(increment)])
        while_statement = statements.While(condition, body)
        if initializer is not None:
            return statements.Block([initializer, while_statement])
        return while_statement

    def while_statement(self) -> statements.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return statements.While(condition, body)

    def if_statement(self) -> statements.Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return statements.If(condition, then_branch, else_branch)

    def print_statement(self) -> statements.Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return statements.Print(value)

    def expression_statement(self) -> statements.Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return statements.Expression(expr)

    def expression(self) -> expressions.Expr:
        return self.assignment()

    def assignment(self) -> expressions.Expr:
        expr = self.parse_or()
        if self.match(TokenType.EQUAL):
            operator = self.previous()
            right = self.assignment()
            if isinstance(expr, expressions.Variable):
                return expressions.Assign(expr.name, right)
            self.error(operator, "Invalid assignment target.")
        return expr

    def left_associative_binary(self, parse_right, match_tokens: List[TokenType], op_constructor=expressions.Binary) -> expressions.Expr:
        '''
        Helper function for binary expressions that are left associative.
        '''
        expr = parse_right()

        while self.match(*match_tokens):
            operator = self.previous()
            right = parse_right()
            expr = op_constructor(expr, operator, right)

        return expr

    def parse_or(self) -> expressions.Expr:
        return self.left_associative_binary(self.parse_and, [TokenType.OR], op_constructor=expressions.Logical)

    def parse_and(self) -> expressions.Expr:
        return self.left_associative_binary(self.equality, [TokenType.AND], op_constructor=expressions.Logical)

    def equality(self) -> expressions.Expr:
        return self.left_associative_binary(self.comparison, [TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL])

    def comparison(self) -> expressions.Expr:
        return self.left_associative_binary(self.term, [TokenType.GREATER, TokenType.GREATER_EQUAL, TokenType.LESS, TokenType.LESS_EQUAL])

    def term(self) -> expressions.Expr:
        return self.left_associative_binary(self.factor, [TokenType.MINUS, TokenType.PLUS])

    def factor(self) -> expressions.Expr:
        return self.left_associative_binary(self.unary, [TokenType.SLASH, TokenType.STAR])

    def unary(self) -> expressions.Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return expressions.Unary(operator, right)
        return self.primary()

    def primary(self) -> expressions.Expr:
        if self.match(TokenType.FALSE):
            return expressions.Literal(False)
        if self.match(TokenType.TRUE):
            return expressions.Literal(True)
        if self.match(TokenType.NIL):
            return expressions.Literal(None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            return expressions.Literal(self.previous().literal)
        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN,
                         "Expect ')' after expression.")
            return expressions.Grouping(expr)
        if self.match(TokenType.IDENTIFIER):
            return expressions.Variable(self.previous())
        self.error(self.peek(), "Expect expression.")

    def consume(self, token_type: TokenType, message: str):
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
            if self.previous().type == TokenType.SEMICOLON:
                return

            token_type = self.peek().type
            if token_type in [TokenType.CLASS, TokenType.FUN, TokenType.VAR, TokenType.FOR, TokenType.IF, TokenType.WHILE, TokenType.PRINT, TokenType.RETURN]:
                return

            self.advance()

    def match(self, *token_types: TokenType) -> bool:
        for token_type in token_types:
            if self.check(token_type):
                self.advance()
                return True
        return False

    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def check(self, token_type: TokenType) -> bool:
        if self.is_at_end():
            return False
        return self.peek().type == token_type

    def is_at_end(self):
        return self.peek().type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        assert self.current > 0
        return self.tokens[self.current - 1]
