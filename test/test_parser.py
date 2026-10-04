from lexer import *
from parser import *


def parse(source: str):
    lexer = Lexer(source)
    tokens = lexer.lex()
    parser = Parser(tokens)
    return parser.parse()


def test_number():
    ast = parse("42")[0]

    assert ast.body.value.value == "42"


def test_addition():
    ast = parse("2 + 3")[0]
    
    assert ast.body.op.value == "+"
    assert ast.body.left.value.value == "2"
    assert ast.body.right.value.value == "3"


def test_subtraction():
    ast = parse("5 - 2")[0]

    assert ast.body.op.value == "-"
    assert ast.body.left.value.value == "5"
    assert ast.body.right.value.value == "2"


def test_multiplication():
    ast = parse("4 * 3")[0]

    assert ast.body.op.value == "*"
    assert ast.body.left.value.value == "4"
    assert ast.body.right.value.value == "3"


def test_division():
    ast = parse("8 / 2")[0]

    assert ast.body.op.value == "/"
    assert ast.body.left.value.value == "8"
    assert ast.body.right.value.value == "2"


def test_operator_precedence():
    # 2 + (3 * 4)
    ast = parse("2 + 3 * 4")[0]

    assert ast.body.op.value == "+"
    assert ast.body.left.value.value == "2"

    assert ast.body.right.op.value == "*"
    assert ast.body.right.left.value.value == "3"
    assert ast.body.right.right.value.value == "4"


def test_operator_precedence_reversed():
    # (2 * 3) + 4
    ast = parse("2 * 3 + 4")[0]

    assert ast.body.op.value == "+"

    assert ast.body.left.op.value == "*"
    assert ast.body.left.left.value.value == "2"
    assert ast.body.left.right.value.value == "3"

    assert ast.body.right.value.value == "4"


def test_multiple_operations():
    # (1 + (2 * 3)) + 4
    ast = parse("1 + 2 * 3 + 4")[0]

    assert ast.body.op.value == "+"
    assert ast.body.left.op.value == "+"

    assert ast.body.left.left.value.value == "1"

    assert ast.body.left.right.op.value == "*"
    assert ast.body.left.right.left.value.value == "2"
    assert ast.body.left.right.right.value.value == "3"

    assert ast.body.right.value.value == "4"


def test_left_associativity():
    # (10 - 3) - 2, NOT 10 - (3 - 2)
    ast = parse("10 - 3 - 2")[0]

    assert ast.body.op.value == "-"

    assert ast.body.left.op.value == "-"
    assert ast.body.left.left.value.value == "10"
    assert ast.body.left.right.value.value == "3"

    assert ast.body.right.value.value == "2"