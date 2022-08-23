import lox_ast
import tokens


class AstPrinter(lox_ast.ExprVisitor):
    def print(self, node: lox_ast.Expr):
        return node.accept(self)

    def parenthesize(self, name: str, *nodes: lox_ast.Expr):
        r = f"{name}("
        for node in nodes:
            r += node.accept(self) + ", "
        r = r[:-2] + ")"
        return r

    def visit_Binary(self, node: lox_ast.Binary):
        return self.parenthesize(node.operator.lexeme, node.left, node.right)

    def visit_Grouping(self, node: lox_ast.Grouping):
        return self.parenthesize("Grouping", node.expression)

    def visit_Literal(self, node: lox_ast.Literal):
        if node.value is None:
            return "Literal(nil)"
        return f"Literal({node.value})"

    def visit_Unary(self, node: lox_ast.Unary):
        return self.parenthesize(node.operator.lexeme, node.right)

    def default(self, node):
        return f"{type(node).__name__}({node})"


def print_ast(node: lox_ast.Expr):
    print(AstPrinter().print(node))


if __name__ == "__main__":
    print(print_ast(lox_ast.Binary(lox_ast.Literal(1), tokens.Token(
        tokens.TokenType.PLUS, "+", None, 1), lox_ast.Literal(2))))
    print("----------------------------------------------------")
    print(print_ast(lox_ast.Grouping(lox_ast.Literal(1))))
    print("----------------------------------------------------")
    print(print_ast(lox_ast.Literal(None)))
    print("----------------------------------------------------")
    print(print_ast(lox_ast.Unary(tokens.Token(
        tokens.TokenType.MINUS, "-", None, 1), lox_ast.Literal(1))))
    print("----------------------------------------------------")
    print(print_ast(lox_ast.Binary(lox_ast.Unary(tokens.Token(
        tokens.TokenType.MINUS, "-", None, 1), lox_ast.Literal(1)), tokens.Token(
            tokens.TokenType.STAR, "*", None, 1), lox_ast.Binary(lox_ast.Literal(
                2), tokens.Token(tokens.TokenType.PLUS, "+", None, 1), lox_ast.Literal(3)))))
