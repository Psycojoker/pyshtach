import os
import sys
import subprocess

from rply import ParserGenerator, LexerGenerator


class ShellException(Exception):
    pass


class Parser():
    def __init__(self):
        lg = LexerGenerator()
        tokens = [
            ("PROTO", r"[a-zA-Z]+://[^ ]+"),
            ("INT", r"\d+"),
            ("STRING", r"'[^']+'|\"[^\"]+\""),
            ("NAME", r"--colors=always"),
            ("PATH", r"([a-zA-Z0-9/._-]|\\ )+"),
            ("PATH", r"~([a-zA-Z0-9/._-]|\\ )*"),
            ("NAME", r"([a-zA-Z0-9_-]|\\ )+"),
            ("SEMICOLON", r";"),
            ("ENDL", r"\r\n"),
            ("ENDL", r"\n"),
        ]

        for token in tokens:
            lg.add(*token)

        lg.ignore(r"[ 	]+")

        pg = ParserGenerator([x[0] for x in tokens])

        @pg.production("main : statements")
        def main(args):
            return args[0]

        @pg.production("statements : statement")
        def statements_one(args):
            expression, = args
            return {
                "type": "statement",
                "content": expression,
            }

        @pg.production("statements : statement separator statements")
        def statements_many(args):
            statement, separtor, statements = args
            return {
                "type": "statement_infix_operator",
                "content": {
                    "left": {
                        "type": "statement",
                        "content": statement,
                    },
                    "right": statements,
                    "operator": separtor,
                }
            }

        @pg.production("separator : SEMICOLON")
        @pg.production("separator : ENDL")
        def separator(args):
            # don't care
            return args[0].value

        @pg.production("statement : atom")
        def expression_one(args):
            atom, = args
            return [atom]

        @pg.production("statement : atom atoms")
        def expression_many(args):
            atom, atoms = args
            return [atom] + atoms

        @pg.production("atoms : atom")
        def atoms_one(args):
            atom, = args
            return [atom]

        @pg.production("atoms : atom atoms")
        def atoms_many(args):
            atom, atoms = args
            return [atom] + atoms

        @pg.production("atom : NAME")
        @pg.production("atom : INT")
        @pg.production("atom : STRING")
        @pg.production("atom : PATH")
        @pg.production("atom : PROTO")
        def atom(args):
            name, = args
            return name.value

        self.pg = pg
        self.lg = lg

        self.lexer = self.lg.build()
        self.parser = self.pg.build()

    def parse(self, foo):
        if not foo:
            return
        return self.parser.parse(self.lexer.lex(foo))


class Shell(object):
    def __init__(self):
        self.parser = Parser()
        self.env = {}
        self.loop = True

    def eval(self, code):
        self.dispatch(self.parser.parse(code))

    def dispatch(self, node):
        getattr(self, "eval_" + node["type"])(node["content"])

    def eval_statement(self, content):
        if content[0] not in self.env:
            raise ShellException("Command not found: %s" % content[0])
        self.env[content[0]](self, content)

    def eval_statement_infix_operator(self, content):
        self.dispatch(content["left"])
        self.dispatch(content["right"])

    def run(self, function):
        function(self)

    def repl(self):
        self.loop = True
        while self.loop:
            try:
                self.eval(raw_input("\033[1;35m%s\033[0m $ " % os.environ["PWD"]).rstrip())
            except EOFError:
                self.loop = False
            except KeyboardInterrupt:
                sys.stdout.write("\n")
            except ShellException as e:
                sys.stderr.write("Error: %s\n" % e)


class Binary(object):
    def __init__(self, binary, path):
        self.path = path
        self.binary = binary

    def __call__(self, shell, arguments):
        process = subprocess.Popen(arguments,
                                   env=os.environ,
                                   stdout=sys.stdout,
                                   stderr=sys.stderr,
                                   stdin=sys.stdin,
                                   cwd=os.environ["PWD"])

        process.wait()


def cd(shell, arguments):
    arguments = arguments[1:]
    if not arguments:
        new_path = os.environ["HOME"]

    elif arguments[0] == "-":
        new_path = os.environ.get("OLDPWD", os.environ["PWD"])

    elif arguments[0].startswith("~"):
        new_path = os.path.expanduser(arguments[0])

    elif not arguments[0].startswith("/"):
        new_path = os.path.join(os.environ["PWD"], arguments[0])

    else:
        new_path = arguments[0]

    new_path = os.path.realpath(new_path)

    if not os.path.exists(new_path):
        raise ShellException("Can't cd to '%s', path doesn't exist" % new_path)

    os.environ["OLDPWD"] = os.environ["PWD"]
    os.environ["PWD"] = new_path


def exit(shell, _):
    shell.loop = False

parse = Parser().parse
shell = Shell()


@shell.run
def add_binaries(shell):
    for path in os.environ["PATH"].split(":"):
        if not os.path.exists(path):
            continue

        for binary in os.listdir(path):
            shell.env[binary] = Binary(binary=binary, path=os.path.join(path, binary))


@shell.run
def add_buildins(shell):
    shell.env["cd"] = cd
    shell.env["exit"] = exit


if __name__ == '__main__':
    shell.repl()
