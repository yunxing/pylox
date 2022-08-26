import lox_ast
from tokens import TokenType, Token
from typing import List, Any


class Interpreter(lox_ast.ExprVisitor):
    def evaluate(self, expr: lox_ast.Expr) -> Any:
        return expr.accept(self)

    def visit_grouping(self, node: lox_ast.Grouping):
        return self.evaluate(node.expression)

    def visit_literal(self, node: lox_ast.Literal):
        return node.value

    def visit_unary(self, node: lox_ast.Unary):
        if node.operator.type == TokenType.MINUS:
            return -self.visit(node.right)
        elif node.operator.type == TokenType.BANG:
            return not self._is_true(self.visit(node.right))

        raise RuntimeError(f"Unknown unary operator {node.operator.lexeme}")

    def visit_binary(self, node: lox_ast.Binary):
        left = self.visit(node.left)
        right = self.visit(node.right)

        node_type = node.operator.type
        if node_type == TokenType.MINUS:
            return left - right
        elif node_type == TokenType.SLASH:
            return left / right
        elif node_type == TokenType.STAR:
            return left * right
        elif node_type == TokenType.PLUS:
            return left + right
        elif node_type == TokenType.GREATER:
            return left > right
        elif node_type == TokenType.GREATER_EQUAL:
            return left >= right
        elif node_type == TokenType.LESS:
            return left < right
        elif node_type == TokenType.LESS_EQUAL:
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
