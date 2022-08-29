import expressions
import statements
import tokens


class AstPrinter(expressions.ExprVisitor, statements.StmtVisitor):
    def print(self, statements):
        for statement in statements:
            print(statement.accept(self))

    def parenthesize(self, name: str, *nodes: expressions.Expr):
        r = f"{name}("
        for node in nodes:
            r += node.accept(self) + ", "
        r = r[:-2] + ")"
        return r

    def visit_expression_stmt(self, node):
        return node.expression.accept(self)

    def visit_print_stmt(self, node):
        return self.parenthesize("Print", node.expression.accept(self))

    def visit_binary_expr(self, node: expressions.Binary):
        return self.parenthesize(node.operator.lexeme, node.left, node.right)

    def visit_grouping_expr(self, node: expressions.Grouping):
        return self.parenthesize("Grouping", node.expression)

    def visit_literal_expr(self, node: expressions.Literal):
        if node.value is None:
            return "Literal(nil)"
        return f"Literal({node.value})"

    def visit_unary_expr(self, node: expressions.Unary):
        return self.parenthesize(node.operator.lexeme, node.right)

    def default_expr(self, node):
        return f"{type(node).__name__}({node})"


def print_ast(statement: statements.Stmt):
    AstPrinter().print(statements)


if __name__ == "__main__":
    print(print_ast(expressions.Binary(expressions.Literal(1), tokens.Token(
        tokens.TokenType.PLUS, "+", None, 1), expressions.Literal(2))))
    print("----------------------------------------------------")
    print(print_ast(expressions.Grouping(expressions.Literal(1))))
    print("----------------------------------------------------")
    print(print_ast(expressions.Literal(None)))
    print("----------------------------------------------------")
    print(print_ast(expressions.Unary(tokens.Token(
        tokens.TokenType.MINUS, "-", None, 1), expressions.Literal(1))))
    print("----------------------------------------------------")
    print(print_ast(expressions.Binary(expressions.Unary(tokens.Token(
        tokens.TokenType.MINUS, "-", None, 1), expressions.Literal(1)), tokens.Token(
            tokens.TokenType.STAR, "*", None, 1), expressions.Binary(expressions.Literal(
                2), tokens.Token(tokens.TokenType.PLUS, "+", None, 1), expressions.Literal(3)))))
