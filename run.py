import argparse
import sys

from scanner import Scanner, ErrorFrame
from lox_parser import Parser
import ast_printer
import interpreter


class Runner:
    def __init__(self, verbose=False):
        self.has_error = False
        self.interpreter = interpreter.Interpreter()
        self.verbose = verbose
        if self.verbose:
            print("Verbose mode enabled.")

    def run_file(self, filepath):
        self._run(open(filepath).read())
        if self.has_error:
            sys.exit(65)

    def run_prompt(self):
        while True:
            # Read a line from stdin, if EOF, break
            try:
                line = input(">>> ")
            except EOFError:
                break
            if line == "":
                continue
            # Run the line
            self._run(line)
            self.had_error = False

    def _run(self, source):
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        if self.maybe_report_errors(scanner.error_frames):
            print("Exiting because of scanner errors.")
            return
        if self.verbose:
            print("Tokens:")
            for token in tokens:
                print(token)

        parser = Parser()
        expr = parser.parse(tokens)
        if self.maybe_report_errors(parser.error_frames):
            print("Exiting because of parser errors.")
            return
        if self.verbose:
            print("AST:")
            ast_printer.print_ast(expr)

        self.interpreter.interpret(expr)
        if self.maybe_report_errors(self.interpreter.error_frames):
            print("Got interpreter errors.")

    def maybe_report_errors(self, error_frames):
        if len(error_frames) > 0:
            for error_frame in error_frames:
                print(error_frame)
            self.has_error = True
            return True


def main():
    argparser = argparse.ArgumentParser(description='Run the program')
    # The argument is the path to the file to be read. The size of the argument is either 0 or 1.
    argparser.add_argument(
        'file', nargs='?', help='The file to be read')
    # Add a cmd line argument to run the program in a verbose mode that prints the AST and tokens.
    # By default, the program runs in a non-verbose mode.
    argparser.add_argument(
        '-v', '--verbose', action='store_true', help='Run in verbose mode')

    args = argparser.parse_args()
    runner = Runner(args.verbose)
    if args.file:
        runner.run_file(args.file)
    else:
        runner.run_prompt()


if __name__ == '__main__':
    main()
