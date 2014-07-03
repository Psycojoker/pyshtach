from rply import ParserGenerator, LexerGenerator

lg = LexerGenerator()
lg.add("NAME", r"[a-zA-Z0-9_-]+")
lg.add("INT", r"\d+")
lg.add("STRING", r"'[^']+'|\"[^\"]+\"")
lg.add("SEMICOLON", r";")
lg.add("ENDL", r"\r\n")
lg.add("ENDL", r"\n")
lg.ignore(r"[ 	]+")

pg = ParserGenerator(["NAME", "INT", "STRING", "SEMICOLON", "ENDL"])

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
def atom(args):
    name, = args
    return name.value

lexer = lg.build()
parser = pg.build()


def parse(foo):
    if not foo:
        return
    return parser.parse(lexer.lex(foo))
