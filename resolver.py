import expressions
import statements
from tokens import TokenType, Token
from typing import List, Any
import dataclasses
from runtime_error import RuntimeError
from return_exception import ReturnException
from environment import Environment


@dataclasses.dataclass
class Scope:
    mapping: dict
    is_function: bool


class Resolver(expressions.ExprVisitor, statements.StmtVisitor):
    def __init__(self):
        self.scopes = []
        self.resolutions = {}

    def visit_block_stmt(self, node: statements.Block):
        self.begin_scope()
        self.resolve(node.statements)
        self.end_scope()

    def resolve_stmts(self, statements: List[statements.Stmt]):
        for statement in statements:
            self.resolve_stmt(statement)

    def resolve_stmt(self, statement: statements.Stmt):
        statement.accept(self)

    def resolve_expr(self, expr: expressions.Expr):
        expr.accept(self)

    def begin_scope(self, is_function: bool = False):
        # Check if previous scope is a function. Pass it to the new scope.
        is_function = is_function or (
            len(self.scopes) > 0 and self.scopes[-1].is_function)
        self.scopes.append(Scope(mapping={}, is_function=is_function))

    def end_scope(self):
        self.scopes.pop()

    # Statements
    def visit_var_stmt(self, node: statements.Var):
        self.declare(node.name)
        if node.initializer is not None:
            self.resolve_expr(node.initializer)

        self.define(node.name)

    def visit_expression_stmt(self, node: statements.Expression):
        self.resolve_expr(node.expression)
        return None

    def visit_if_stmt(self, node: statements.If):
        self.resolve_expr(node.condition)
        self.resolve_stmt(node.then_branch)
        if node.else_branch is not None:
            self.resolve_stmt(node.else_branch)

    def visit_function_stmt(self, node: statements.Function):
        self.declare(node.name)
        self.define(node.name)

        self.resolve_function(node)

    def visit_print_stmt(self, node: statements.Print):
        self.resolve_expr(node.expression)
        return None

    def visit_while_stmt(self, node: statements.While):
        self.resolve_expr(node.condition)
        self.resolve_stmt(node.body)
        return None

    def visit_return_stmt(self, node: statements.Return):
        # If current scope is not in a function, raise error.
        if len(self.scopes) == 0 or not self.scopes[-1].is_function:
            raise RuntimeError(
                node.keyword, "Cannot return from top-level code.")
        if node.value is not None:
            self.resolve_expr(node.value)
        return None

    # Expressions

    def visit_binary_expr(self, node: expressions.Binary):
        self.resolve_expr(node.left)
        self.resolve_expr(node.right)

    def visit_call_expr(self, node: expressions.Call):
        self.resolve_expr(node.callee)
        for argument in node.arguments:
            self.resolve_expr(argument)

    def visit_grouping_expr(self, node: expressions.Call):
        self.resolve_expr(node.expression)

    def visit_literal_expr(self, node: expressions.Literal):
        return None

    def visit_logical_expr(self, node: expressions.Logical):
        self.resolve_expr(node.left)
        self.resolve_expr(node.right)

    def visit_unary_expr(self, node: expressions.Unary):
        self.resolve_expr(node.right)

    def visit_assign_expr(self, node: expressions.Assign):
        self.resolve_expr(node.value)
        self.resolve_local(node, node.name)
        return None

    def visit_variable_expr(self, node: expressions.Variable):
        if (len(self.scopes) > 0 or
                self.scopes[-1].mapping[node.name.lexeme] == False):
            raise RuntimeError(
                node.name, "Cannot read local variable in its own initializer.")

        self.resolve_local(node, node.name)
        return None

    # Helpers
    def declare(self, name: Token):
        if not self.scopes:
            return
        scope = self.scopes[-1]
        if name.lexeme in scope.mapping:
            raise RuntimeError(
                name, "Variable with this name already declared in this scope.")
        scope.mapping[name.lexeme] = False

    def define(self, name: Token):
        if not self.scopes:
            return

        self.scopes[-1].mapping[name.lexeme] = True

    def resolve_local(self, expr: expressions.Expr, name: Token):
        for i in range(len(self.scopes)):
            scope = self.scopes[len(self.scopes) - 1 - i].mapping
            if name.lexeme in scope:
                self.add_resolve_result(expr, i)
                return

    def add_resolve_result(self, expr: expressions.Expr, depth: int):
        self.resolutions[expr] = depth

    def resolve_function(self, function: statements.Function):
        self.begin_scope(True)
        for param in function.params:
            self.declare(param)
            self.define(param)
        self.resolve_stmts(function.body)
        self.end_scope()
