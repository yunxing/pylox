# This file was automatically generated by gen_ast.py.
from tokens import Token
from typing import List, Any
from expressions import Expr

class StmtVisitor:
    def visit_expression_stmt(self, node : "Expression"):
        pass
    def visit_if_stmt(self, node : "If"):
        pass
    def visit_block_stmt(self, node : "Block"):
        pass
    def visit_var_stmt(self, node : "Var"):
        pass
    def visit_print_stmt(self, node : "Print"):
        pass
    def visit_while_stmt(self, node : "While"):
        pass
    def default_stmt(self, node):
        pass

class Stmt:
    def accept(self, visitor : StmtVisitor):
        if isinstance(self, Expression):
            return visitor.visit_expression_stmt(self)
        if isinstance(self, If):
            return visitor.visit_if_stmt(self)
        if isinstance(self, Block):
            return visitor.visit_block_stmt(self)
        if isinstance(self, Var):
            return visitor.visit_var_stmt(self)
        if isinstance(self, Print):
            return visitor.visit_print_stmt(self)
        if isinstance(self, While):
            return visitor.visit_while_stmt(self)
        return visitor.default_stmt(self)

class Expression(Stmt):
    def __init__(self , expression : Expr):
        self.expression : Expr = expression
    def __str__(self):
        r = "Expression("
        r += f"expression : Expr = "
        r += str(self.expression)
        r += ","

        r += ")"
        return r
class If(Stmt):
    def __init__(self , condition : Expr, then_branch : Stmt, else_branch : Stmt):
        self.condition : Expr = condition
        self.then_branch : Stmt = then_branch
        self.else_branch : Stmt = else_branch
    def __str__(self):
        r = "If("
        r += f"condition : Expr = "
        r += str(self.condition)
        r += ","

        r += f"then_branch : Stmt = "
        r += str(self.then_branch)
        r += ","

        r += f"else_branch : Stmt = "
        r += str(self.else_branch)
        r += ","

        r += ")"
        return r
class Block(Stmt):
    def __init__(self , statements : List[Stmt]):
        self.statements : List[Stmt] = statements
    def __str__(self):
        r = "Block("
        r += f"statements : List[Stmt] = "
        r += str(self.statements)
        r += ","

        r += ")"
        return r
class Var(Stmt):
    def __init__(self , name : Token, initializer : Expr):
        self.name : Token = name
        self.initializer : Expr = initializer
    def __str__(self):
        r = "Var("
        r += f"name : Token = "
        r += str(self.name)
        r += ","

        r += f"initializer : Expr = "
        r += str(self.initializer)
        r += ","

        r += ")"
        return r
class Print(Stmt):
    def __init__(self , expression : Expr):
        self.expression : Expr = expression
    def __str__(self):
        r = "Print("
        r += f"expression : Expr = "
        r += str(self.expression)
        r += ","

        r += ")"
        return r
class While(Stmt):
    def __init__(self , condition : Expr, body : Stmt):
        self.condition : Expr = condition
        self.body : Stmt = body
    def __str__(self):
        r = "While("
        r += f"condition : Expr = "
        r += str(self.condition)
        r += ","

        r += f"body : Stmt = "
        r += str(self.body)
        r += ","

        r += ")"
        return r

