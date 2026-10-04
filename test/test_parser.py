from lexer import *
from parser import *


def parse(source: str):
    lexer = Lexer(source)
    tokens = lexer.lex()
    parser = Parser(tokens)
    return parser.parse_expression()


def test_number():
    ast = parse("42")

    assert ast.value.value == "42"


def test_addition():
    ast = parse("2 + 3")

    assert ast.op.value == "+"
    assert ast.left.value.value == "2"
    assert ast.right.value.value == "3"


def test_subtraction():
    ast = parse("5 - 2")

    assert ast.op.value == "-"
    assert ast.left.value.value == "5"
    assert ast.right.value.value == "2"


def test_multiplication():
    ast = parse("4 * 3")

    assert ast.op.value == "*"
    assert ast.left.value.value == "4"
    assert ast.right.value.value == "3"


def test_division():
    ast = parse("8 / 2")

    assert ast.op.value == "/"
    assert ast.left.value.value == "8"
    assert ast.right.value.value == "2"


def test_operator_precedence():
    # 2 + (3 * 4)
    ast = parse("2 + 3 * 4")

    assert ast.op.value == "+"
    assert ast.left.value.value == "2"

    assert ast.right.op.value == "*"
    assert ast.right.left.value.value == "3"
    assert ast.right.right.value.value == "4"


def test_operator_precedence_reversed():
    # (2 * 3) + 4
    ast = parse("2 * 3 + 4")

    assert ast.op.value == "+"

    assert ast.left.op.value == "*"
    assert ast.left.left.value.value == "2"
    assert ast.left.right.value.value == "3"

    assert ast.right.value.value == "4"


def test_multiple_operations():
    # (1 + (2 * 3)) + 4
    ast = parse("1 + 2 * 3 + 4")

    assert ast.op.value == "+"
    assert ast.left.op.value == "+"

    assert ast.left.left.value.value == "1"

    assert ast.left.right.op.value == "*"
    assert ast.left.right.left.value.value == "2"
    assert ast.left.right.right.value.value == "3"

    assert ast.right.value.value == "4"


def test_left_associativity():
    # (10 - 3) - 2, NOT 10 - (3 - 2)
    ast = parse("10 - 3 - 2")

    assert ast.op.value == "-"

    assert ast.left.op.value == "-"
    assert ast.left.left.value.value == "10"
    assert ast.left.right.value.value == "3"

    assert ast.right.value.value == "2"