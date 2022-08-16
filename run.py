import argparse
import sys


class Runner:
    def __init__(self):
        self.has_error = False

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

    def _run(source): pass

    def error(self, lineno, message):
        # Print the error message and line number to stderr
        print(f"{lineno}: {message}", file=sys.stderr)
        self.has_error = True


def main():
    argparser = argparse.ArgumentParser(description='Run the program')
    # The argument is the path to the file to be read. The size of the argument is either 0 or 1.
    argparser.add_argument(
        'file', nargs='?', help='The file to be read')
    args = argparser.parse_args()
    runner = Runner()
    if args.file:
        runner.run_file(args.file)
    else:
        runner.run_prompt()


if __name__ == '__main__':
    main()
