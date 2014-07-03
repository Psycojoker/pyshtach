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
