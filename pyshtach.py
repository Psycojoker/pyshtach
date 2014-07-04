from rply import ParserGenerator, LexerGenerator

class Parser():
    def __init__(self):
        lg = LexerGenerator()
        tokens = [
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
            return [expression]

        @pg.production("statements : statement separator statements")
        def statements_many(args):
            statement, _, statements = args
            return [statement] + statements

        @pg.production("separator : SEMICOLON")
        @pg.production("separator : ENDL")
        def separator(args):
            # don't care
            return None

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


parse = Parser().parse
