import expressions
import statements
from tokens import TokenType, Token
from typing import List, Any
import dataclasses
from runtime_error import RuntimeError
from return_exception import ReturnException
from environment import Environment
import time
from resolver import Resolver


@dataclasses.dataclass
class ErrorFrame:
    line: int
    message: str

    def __str__(self):
        return f"{self.line}: {self.message}"


class Callable:
    def arity(self):
        raise NotImplementedError()

    def call(self, interpreter, args):
        raise NotImplementedError()


class LoxFunction(Callable):
    def __init__(self, declaration: statements.Function, closure: Environment) -> None:
        self.declaration = declaration
        self._arity = len(declaration.params)
        self._closure = closure

    def call(self, interpreter, args):
        environment = Environment(self._closure)
        for i in range(len(args)):
            environment.define(self.declaration.params[i].lexeme, args[i])
        try:
            interpreter.execute_block(self.declaration.body, environment)
        except ReturnException as e:
            return e.value
        return None

    def arity(self):
        return self._arity

    def __str__(self) -> str:
        return f"<fn {self.declaration.name.lexeme}, arity {self.arity()}>"


class LoxInstance:
    def __init__(self, klass: 'LoxClass') -> None:
        self.klass = klass
        self.fields = {}

    def get_field(self, name: Token):
        if name.lexeme in self.fields:
            return self.fields[name.lexeme]
        raise RuntimeError(f"Undefined property '{name.lexeme}'.")

    def set_field(self, name: Token, value: Any):
        self.fields[name.lexeme] = value

    def __str__(self):
        return f"<instance of {self.klass.name}>"


class LoxClass(Callable):
    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self) -> str:
        return self.name

    def call(self, interpreter, args):
        instance = LoxInstance(self)
        return instance

    def arity(self):
        return 0


class Interpreter(expressions.ExprVisitor, statements.StmtVisitor):
    def __init__(self) -> None:
        self.globals = self.global_env()
        self.environment = self.globals
        self.error_frames = []

    def global_env(self):
        class Clock(Callable):
            def arity(self):
                return 0

            def call(self, interpreter, args):
                # Returns the current system time in milliseconds.
                return time.time()

            def __str__(self):
                return "<native fn> Clock()"

        r = Environment()
        r.define("clock", Clock())
        return r

    def evaluate(self, expr: expressions.Expr) -> Any:
        return expr.accept(self)

    def execute(self, stmt: statements.Stmt) -> None:
        stmt.accept(self)

    def interpret(self, statements: List[statements.Stmt]) -> None:
        resolver = Resolver()
        resolver.resolve_stmts(statements)
        self.locals = resolver.resolutions
        try:
            self.error_frames = []
            for statement in statements:
                self.execute(statement)
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

    # Statements
    def visit_var_stmt(self, node: statements.Var):
        value = None
        if node.initializer is not None:
            value = self.evaluate(node.initializer)
        self.environment.define(node.name.lexeme, value)
        return None

    def visit_function_stmt(self, node: statements.Function):
        f = LoxFunction(node, self.environment)
        self.environment.define(node.name.lexeme, f)
        return None

    def visit_return_stmt(self, node: statements.Return):
        value = None
        if node.value is not None:
            value = self.evaluate(node.value)
        raise ReturnException(value)

    def visit_expression_stmt(self, node: statements.Expression):
        return self.evaluate(node.expression)

    def visit_print_stmt(self, node: statements.Print):
        value = self.evaluate(node.expression)
        print(self.stringify(value))

    def visit_block_stmt(self, node: statements.Block):
        self.execute_block(node.statements, Environment(self.environment))

    def visit_if_stmt(self, node: statements.If):
        if self._is_true(self.evaluate(node.condition)):
            self.execute(node.then_branch)
        elif node.else_branch is not None:
            self.execute(node.else_branch)
        return None

    def visit_while_stmt(self, node: statements.While):
        while self._is_true(self.evaluate(node.condition)):
            self.execute(node.body)
        return None

    def visit_class_stmt(self, node: statements.Class):
        self.environment.define(node.name.lexeme, None)
        klass = LoxClass(node.name.lexeme)
        self.environment.assign(node.name, klass)
    # Expressions

    def visit_assign_expr(self, node: expressions.Assign):
        value = self.evaluate(node.value)
        distance = self.locals.get(node, None)
        if distance is not None:
            self.environment.assign_at(distance, node.name, value)
        else:
            self.globals.assign(node.name, value)
        return value

    def visit_call_expr(self, node: expressions.Call):
        callee = self.evaluate(node.callee)
        if not isinstance(callee, Callable):
            raise RuntimeError(
                node.paren, "Can only call functions and classes.")
        arguments = [self.evaluate(arg) for arg in node.arguments]
        if len(arguments) != callee.arity():
            raise RuntimeError(
                node.paren, f"Expected {callee.arity()} arguments but got {len(arguments)}.")
        return callee.call(self, arguments)

    def visit_grouping_expr(self, node: expressions.Grouping):
        return self.evaluate(node.expression)

    def visit_variable_expr(self, node: expressions.Variable):
        return self._lookup_variable(node.name, node)

    def visit_literal_expr(self, node: expressions.Literal):
        return node.value

    def visit_logical_expr(self, node: expressions.Logical):
        left = self.evaluate(node.left)
        if node.operator.type == TokenType.OR:
            if self._is_true(left):
                return left
        else:
            if not self._is_true(left):
                return left
        return self.evaluate(node.right)

    def visit_unary_expr(self, node: expressions.Unary):
        if node.operator.type == TokenType.MINUS:
            return -self.evaluate(node.right)
        elif node.operator.type == TokenType.BANG:
            return not self._is_true(self.evaluate(node.right))

        raise RuntimeError(f"Unknown unary operator {node.operator.lexeme}")

    def visit_binary_expr(self, node: expressions.Binary):
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

    def visit_get_expr(self, node: expressions.Get):
        obj = self.evaluate(node.object)
        if isinstance(obj, LoxInstance):
            return obj.get_field(node.name)
        raise RuntimeError(node.name, "Only instances have properties.")

    def visit_set_expr(self, node: expressions.Set):
        obj = self.evaluate(node.object)
        if not isinstance(obj, LoxInstance):
            raise RuntimeError(
                node.name, f"Only instances have fields. Got {obj.__class__.__name__}.")

        if False:
            if node.name.lexeme not in obj.fields:
                raise RuntimeError(
                    node.name, f"Instance has no field {node.name.lexeme}.")

        value = self.evaluate(node.value)
        obj.set_field(node.name, value)

    # Helpers.

    def execute_block(self, statements: List[statements.Stmt], environment: Environment):
        previous = self.environment
        try:
            self.environment = environment
            for statement in statements:
                self.execute(statement)
        finally:
            self.environment = previous

    def _lookup_variable(self, name: Token, expr: expressions.Expr):
        distance = self.locals.get(expr, None)
        if distance is not None:
            return self.environment.get_at(distance, name.lexeme)
        else:
            return self.globals.get(name)

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
