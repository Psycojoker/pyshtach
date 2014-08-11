import os
import operator
import subprocess

from rply import ParserGenerator, LexerGenerator

class Parser():
    def __init__(self):
        lg = LexerGenerator()
        tokens = [
            ("PROTO", r"[a-zA-Z]+://[^ ]+"),
            ("NAME", r"([a-zA-Z0-9_-]|\\ )+"),
            ("INT", r"\d+"),
            ("STRING", r"'[^']+'|\"[^\"]+\""),
            ("PATH", r"([a-zA-Z0-9/._-]|\\ )+"),
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
        self.callables = reduce(operator.add, map(os.listdir, filter(os.path.exists, os.environ["PATH"].split(":"))), [])

    def eval(self, code):
        self.dispatch(self.parser.parse(code))

    def dispatch(self, node):
        getattr(self, "eval_" + node["type"])(node["content"])

    def eval_statement(self, content):
        if content[0] not in self.callables:
            raise Exception("Command not found: %s" % content[0])
        subprocess.call(content)

    def eval_statement_infix_operator(self, content):
        self.dispatch(content["left"])
        self.dispatch(content["right"])


parse = Parser().parse
shell = Shell()
