from enum import Enum, auto
from typing import Any


class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()


class TokenType(AutoName):
    # Single-character tokens
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()
    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()
    QUESTION = auto()
    # One or two character tokens
    BANG = auto()
    BANG_EQUAL = auto()
    EQUAL = auto()
    EQUAL_EQUAL = auto()
    GREATER = auto()
    GREATER_EQUAL = auto()
    LESS = auto()
    LESS_EQUAL = auto()
    # Literals
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()
    # Keywords
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()
    EOF = auto()


class ReservedKeyword(AutoName):
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()
    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

# check if a string is a reserved keyword


def is_reserved_keyword(string) -> bool:
    # Get the set of values for the enum ReservedKeyword
    values = ReservedKeyword.__members__.values()
    # Check if string is in the value field of the ReservedKeyword enum
    return string in set(v.value for v in ReservedKeyword.__members__.values())


def get_reserved_keyword_as_token(string) -> TokenType:
    return TokenType[string.upper()]


class Token:
    def __init__(self, type: TokenType, lexeme: str, literal: Any, line: int):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def __str__(self):
        if self.literal is None:
            return f"{self.type} lexeme: {self.lexeme}"
        return f"{self.type} lexeme: {self.lexeme} literal: {self.literal}"
