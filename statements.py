# This file was automatically generated by gen_ast.py.
from tokens import Token
from typing import List, Any
from expressions import Expr


class StmtVisitor:
    def visit_expression_stmt(self, node: "Expression"):
        pass

    def visit_print_stmt(self, node: "Print"):
        pass

    def default_stmt(self, node):
        pass


class Stmt:
    def accept(self, visitor: StmtVisitor):
        if isinstance(self, Expression):
            return visitor.visit_expression_stmt(self)
        if isinstance(self, Print):
            return visitor.visit_print_stmt(self)
        return visitor.default_stmt(self)


class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    def __str__(self):
        r = "Expression("
        r += f"expression : Expr = "
        r += str(self.expression)
        r += ","

        r += ")"
        return r


class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression: Expr = expression

    def __str__(self):
        r = "Print("
        r += f"expression : Expr = "
        r += str(self.expression)
        r += ","

        r += ")"
        return r
