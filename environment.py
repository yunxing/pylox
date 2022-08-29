from runtime_error import RuntimeError
from typing import Any
from tokens import Token


class Environment:
    def __init__(self) -> None:
        self.values = {}

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
        else:
            raise RuntimeError(
                name, f"Undefined variable assignment: {name.lexeme}.")

    def define(self, name: Token, value: Any) -> None:
        self.values[name.lexeme] = value

    def get(self, name: Token) -> Any:
        try:
            return self.values[name.lexeme]
        except KeyError:
            raise RuntimeError(name, f"Undefined variable: {name.lexeme}.")
