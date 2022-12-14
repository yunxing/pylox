from runtime_error import RuntimeError
from typing import Any
from tokens import Token


class Environment:
    def __init__(self, enclosing=None) -> None:
        self.values = {}
        self.enclosing = enclosing

    def assign(self, name: Token, value: Any) -> None:
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise RuntimeError(
            name, f"Undefined variable assignment: {name.lexeme}.")

    def define(self, name: str, value: Any) -> None:
        self.values[name] = value

    def get(self, name: Token) -> Any:
        if name.lexeme in self.values:
            return self.values[name.lexeme]

        if self.enclosing is not None:
            return self.enclosing.get(name)
        raise RuntimeError(name, f"Undefined variable: {name.lexeme}.")

    def get_at(self, distance: int, name: str) -> Any:
        return self.ancestor(distance).values[name]

    def ancestor(self, distance: int) -> "Environment":
        environment = self
        for _ in range(distance):
            environment = environment.enclosing
        return environment

    def assign_at(self, distance: int, name: Token, value: Any) -> None:
        self.ancestor(distance).values[name.lexeme] = value
