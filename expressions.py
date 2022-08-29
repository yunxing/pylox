# This file was automatically generated by gen_ast.py.
from tokens import Token
from typing import List, Any

class ExprVisitor:
    def visit_binary_expr(self, node : "Binary"):
        pass
    def visit_grouping_expr(self, node : "Grouping"):
        pass
    def visit_literal_expr(self, node : "Literal"):
        pass
    def visit_unary_expr(self, node : "Unary"):
        pass
    def default_expr(self, node):
        pass

class Expr:
    def accept(self, visitor : ExprVisitor):
        if isinstance(self, Binary):
            return visitor.visit_binary_expr(self)
        if isinstance(self, Grouping):
            return visitor.visit_grouping_expr(self)
        if isinstance(self, Literal):
            return visitor.visit_literal_expr(self)
        if isinstance(self, Unary):
            return visitor.visit_unary_expr(self)
        return visitor.default_expr(self)

class Binary(Expr):
    def __init__(self , left : Expr, operator : Token, right : Expr):
        self.left : Expr = left
        self.operator : Token = operator
        self.right : Expr = right
    def __str__(self):
        r = "Binary("
        r += f"left : Expr = "
        r += str(self.left)
        r += ","

        r += f"operator : Token = "
        r += str(self.operator)
        r += ","

        r += f"right : Expr = "
        r += str(self.right)
        r += ","

        r += ")"
        return r
class Grouping(Expr):
    def __init__(self , expression : Expr):
        self.expression : Expr = expression
    def __str__(self):
        r = "Grouping("
        r += f"expression : Expr = "
        r += str(self.expression)
        r += ","

        r += ")"
        return r
class Literal(Expr):
    def __init__(self , value : Any):
        self.value : Any = value
    def __str__(self):
        r = "Literal("
        r += f"value : Any = "
        r += str(self.value)
        r += ","

        r += ")"
        return r
class Unary(Expr):
    def __init__(self , operator : Token, right : Expr):
        self.operator : Token = operator
        self.right : Expr = right
    def __str__(self):
        r = "Unary("
        r += f"operator : Token = "
        r += str(self.operator)
        r += ","

        r += f"right : Expr = "
        r += str(self.right)
        r += ","

        r += ")"
        return r

