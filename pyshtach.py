from rply import ParserGenerator, LexerGenerator

lg = LexerGenerator()
lg.add("NAME", r"[a-zA-Z0-9_-]+")
lg.add("INT", r"\d+")
lg.ignore(r"\s+")

pg = ParserGenerator(["NAME", "INT"])

@pg.production("main : expression")
def main(args):
    expression, = args
    return expression

@pg.production("expression : atom")
def expression_one(args):
    atom, = args
    return [atom]

@pg.production("expression : atom atoms")
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
def atom(args):
    name, = args
    return name.value

lexer = lg.build()
parser = pg.build()


def parse(foo):
    if not foo:
        return
    return parser.parse(lexer.lex(foo))
