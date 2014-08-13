from pyshtach import parse


def test_empty():
    parse("")


def test_word():
    parse("foobar")


def test_words():
    parse("badger mushroom snake")


def test_int():
    parse("1 2 3")


def test_dashed_words():
    parse("a -b -drf --foo")


def test_args_with_equal():
    parse("a --colors=always")


def test_string():
    parse('"foor" "bar" \'baz\'')


def test_many_statements():
    assert parse('foo; bar\nbaz')


def test_escaped_space():
    assert parse("a\\ b")["type"] == "statement"


def test_tab_escaped():
    parse("a	b")


def test_path_atom():
    parse("a/b/c/../pouet")


def test_proto():
    parse("ssh://pouet")
    parse("http://pouet")
    parse("http://pouet.com:2000/qsd.php")


def test_infix_statement_operator_return_both_statements():
    stuff = parse("a; b")
    assert stuff["content"]["left"]["type"] == "statement"
    assert stuff["content"]["right"]["type"] == "statement"
