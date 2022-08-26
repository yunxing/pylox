import expressions
from tokens import TokenType, Token
from typing import List, Any
import dataclasses


class RuntimeError(Exception):
    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token


@dataclasses.dataclass
class ErrorFrame:
    line: int
    message: str

    def __str__(self):
        return f"{self.line}: {self.message}"


class Interpreter(expressions.ExprVisitor):
    def __init__(self) -> None:
        self.error_frames = []

    def evaluate(self, expr: expressions.Expr) -> Any:
        return expr.accept(self)

    def interpret(self, expr: expressions.Expr) -> None:
        try:
            self.error_frames = []
            value = self.evaluate(expr)
            print(self.stringify(value))
        except RuntimeError as error:
            self._had_runtime_error = True
            self.error_frames.append(ErrorFrame(
                error.token.line, error.message))
            return

    def stringify(self, value: Any) -> str:
        if value is None:
            return "nil"
        if isinstance(value, float):
            return f"{value:.2f}"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)

    def visit_grouping(self, node: expressions.Grouping):
        return self.evaluate(node.expression)

    def visit_literal(self, node: expressions.Literal):
        return node.value

    def visit_unary(self, node: expressions.Unary):
        if node.operator.type == TokenType.MINUS:
            return -self.evaluate(node.right)
        elif node.operator.type == TokenType.BANG:
            return not self._is_true(self.evaluate(node.right))

        raise RuntimeError(f"Unknown unary operator {node.operator.lexeme}")

    def visit_binary(self, node: expressions.Binary):
        left = self.evaluate(node.left)
        right = self.evaluate(node.right)

        node_type = node.operator.type
        if node_type == TokenType.MINUS:
            self._check_number_operands(node.operator, left, right)
            return left - right
        elif node_type == TokenType.SLASH:
            self._check_number_operands(node.operator, left, right)
            return left / right
        elif node_type == TokenType.STAR:
            self._check_number_operands(node.operator, left, right)
            return left * right
        elif node_type == TokenType.PLUS:
            if isinstance(left, float) and isinstance(right, float):
                return left + right
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            raise RuntimeError(node.operator,
                               "Operands must be two numbers or two strings.")
        elif node_type == TokenType.GREATER:
            self._check_number_operands(node.operator, left, right)
            return left > right
        elif node_type == TokenType.GREATER_EQUAL:
            self._check_number_operands(node.operator, left, right)
            return left >= right
        elif node_type == TokenType.LESS:
            self._check_number_operands(node.operator, left, right)
            return left < right
        elif node_type == TokenType.LESS_EQUAL:
            self._check_number_operands(node.operator, left, right)
            return left <= right
        elif node_type == TokenType.BANG_EQUAL:
            return not self._is_equal(left, right)
        elif node_type == TokenType.EQUAL_EQUAL:
            return self._is_equal(left, right)
        raise RuntimeError(f"Unknown binary operator {node.operator.lexeme}")

    def _is_true(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        return True

    def _is_equal(self, a, b):
        if a is None and b is None:
            return True
        if a is None or b is None:
            return False
        return a == b

    def _check_number_operand(self, operator: Token, operand: Any):
        if not isinstance(operand, float):
            raise RuntimeError(operator,
                               f"Operand must be a number. Got {type(operand)} instead.")

    def _check_number_operands(self, operator: Token, left: Any, right: Any):
        if not isinstance(left, float) or not isinstance(right, float):
            raise RuntimeError(operator,
                               f"Operands must be numbers. Got {type(left)} and {type(right)} instead.")
