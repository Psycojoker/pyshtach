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


def test_string():
    parse('"foor" "bar" \'baz\'')


def test_many_statements():
    assert len(parse('foo; bar\nbaz')) == 3


def test_escaped_space():
    assert len(parse("a\\ b")[0]) == 1


def test_tab_escaped():
    parse("a	b")


def test_path_atom():
    parse("a/b/c/../pouet")


def test_proto():
    parse("ssh://pouet")
    parse("http://pouet")
    parse("http://pouet.com:2000/qsd.php")
