from lexer import *
from parser import *
import pytest


def parse(source: str) -> list[Function]:
    lexer = Lexer(source)
    tokens = lexer.lex()
    parser = Parser(tokens)
    return parser.parse()


def parse_expr(source: str) -> Statement:
    return parse(f"fn test() {source}")[0].body


def test_number():
    expr = parse_expr("42")

    assert expr.expr.value.value == "42"


def test_identifier():
    expr = parse_expr("x")

    assert expr.value.value == "x"


def test_addition():
    expr = parse_expr("2 + 3")

    assert expr.expr.op.value == "+"
    assert expr.expr.left.value.value == "2"
    assert expr.expr.right.value.value == "3"


def test_subtraction():
    expr = parse_expr("5 - 2")

    assert expr.expr.op.value == "-"
    assert expr.expr.left.value.value == "5"
    assert expr.expr.right.value.value == "2"


def test_multiplication():
    expr = parse_expr("4 * 3")

    assert expr.expr.op.value == "*"
    assert expr.expr.left.value.value == "4"
    assert expr.expr.right.value.value == "3"


def test_division():
    expr = parse_expr("8 / 2")

    assert expr.expr.op.value == "/"
    assert expr.expr.left.value.value == "8"
    assert expr.expr.right.value.value == "2"


def test_less_than():
    expr = parse_expr("2 < 3")

    assert expr.expr.op.value == "<"
    assert expr.expr.left.value.value == "2"
    assert expr.expr.right.value.value == "3"


def test_greater_than():
    expr = parse_expr("3 > 2")

    assert expr.expr.op.value == ">"
    assert expr.expr.left.value.value == "3"
    assert expr.expr.right.value.value == "2"


def test_equal():
    expr = parse_expr("2 == 2")

    assert expr.expr.op.value == "=="
    assert expr.expr.left.value.value == "2"
    assert expr.expr.right.value.value == "2"


def test_parentheses():
    expr = parse_expr("(2 + 3) * 4")

    assert expr.expr.op.value == "*"

    assert expr.expr.left.op.value == "+"
    assert expr.expr.left.left.value.value == "2"
    assert expr.expr.left.right.value.value == "3"

    assert expr.expr.right.value.value == "4"


def test_operator_precedence():
    # 2 + (3 * 4)
    expr = parse_expr("2 + 3 * 4")

    assert expr.expr.op.value == "+"
    assert expr.expr.left.value.value == "2"

    assert expr.expr.right.op.value == "*"
    assert expr.expr.right.left.value.value == "3"
    assert expr.expr.right.right.value.value == "4"


def test_operator_precedence_reversed():
    # (2 * 3) + 4
    expr = parse_expr("2 * 3 + 4")

    assert expr.expr.op.value == "+"

    assert expr.expr.left.op.value == "*"
    assert expr.expr.left.left.value.value == "2"
    assert expr.expr.left.right.value.value == "3"

    assert expr.expr.right.value.value == "4"


def test_multiple_operations():
    # (1 + (2 * 3)) + 4
    expr = parse_expr("1 + 2 * 3 + 4")

    assert expr.expr.op.value == "+"
    assert expr.expr.left.op.value == "+"

    assert expr.expr.left.left.value.value == "1"

    assert expr.expr.left.right.op.value == "*"
    assert expr.expr.left.right.left.value.value == "2"
    assert expr.expr.left.right.right.value.value == "3"

    assert expr.expr.right.value.value == "4"


def test_left_associativity():
    expr = parse_expr("10 - 3 - 2")

    assert expr.expr.op.value == "-"

    assert expr.expr.left.op.value == "-"
    assert expr.expr.left.left.value.value == "10"
    assert expr.expr.left.right.value.value == "3"

    assert expr.expr.right.value.value == "2"


def test_function_call():
    call = parse_expr("foo(42)")

    assert call.callee.value.value == "foo"
    assert len(call.arguments) == 1
    assert call.arguments[0].value.value == "42"


def test_function_call_multiple_arguments():
    call = parse_expr("foo(1, 2, 3)")

    assert call.callee.value.value == "foo"
    assert len(call.arguments) == 3

    assert call.arguments[0].value.value == "1"
    assert call.arguments[1].value.value == "2"
    assert call.arguments[2].value.value == "3"


def test_function_call_expr_arguments():
    call = parse_expr("foo(1 + 2, 3 * 4)")

    assert call.arguments[0].op.value == "+"
    assert call.arguments[0].left.value.value == "1"
    assert call.arguments[0].right.value.value == "2"

    assert call.arguments[1].op.value == "*"
    assert call.arguments[1].left.value.value == "3"
    assert call.arguments[1].right.value.value == "4"


def test_if_expr():
    if_expr = parse_expr("if 1 < 2 3")

    assert if_expr.condition.op.value == "<"
    assert if_expr.condition.left.value.value == "1"
    assert if_expr.condition.right.value.value == "2"

    assert if_expr.then_expr.expr.value.value == "3"
    assert if_expr.else_expr is None


def test_if_else_expr():
    if_expr = parse_expr("if 1 < 2 3 else 4")

    assert if_expr.condition.op.value == "<"
    assert if_expr.then_expr.expr.value.value == "3"
    assert if_expr.else_expr.expr.value.value == "4"


def test_function():
    function = parse("fn add(a, b) a + b")[0]

    assert function.name == "add"
    assert len(function.parameters) == 2

    assert function.parameters[0].value == "a"
    assert function.parameters[1].value == "b"

    assert function.body.op.value == "+"
    assert function.body.left.value.value == "a"
    assert function.body.right.value.value == "b"


def test_function_no_parameters():
    function = parse("fn foo() 42")[0]

    assert function.name == "foo"
    assert function.parameters == []
    assert function.body.expr.value.value == "42"


def test_multiple_functions():
    ast = parse(
        """
        fn add(a, b) a + b
        fn sub(a, b) a - b
        """
    )

    assert len(ast) == 2

    assert ast[0].name == "add"
    assert ast[1].name == "sub"
    

def test_unary_minus_number():
    expr = parse_expr("-5")

    assert expr.expr.op.value == "-"
    assert expr.expr.left.value.value == "0"
    assert expr.expr.right.value.value == "5"


def test_unary_minus_identifier():
    expr = parse_expr("-x")

    assert expr.expr.op.value == "-"
    assert expr.expr.left.value.value == "0"
    assert expr.expr.right.value.value == "x"


def test_unary_minus_parenthesized_expr():
    expr = parse_expr("-(2 + 3)")

    assert expr.expr.op.value == "-"
    assert expr.expr.left.value.value == "0"

    assert expr.expr.right.op.value == "+"
    assert expr.expr.right.left.value.value == "2"
    assert expr.expr.right.right.value.value == "3"


def test_double_unary_minus():
    expr = parse_expr("--5")

    assert expr.expr.op.value == "-"
    assert expr.expr.left.value.value == "0"

    inner = expr.expr.right
    assert inner.op.value == "-"
    assert inner.left.value.value == "0"
    assert inner.right.value.value == "5"


def test_unary_minus_precedence():
    # (-2) * 3
    expr = parse_expr("-2 * 3")

    assert expr.expr.op.value == "*"
    assert expr.expr.left.op.value == "-"
    assert expr.expr.left.right.value.value == "2"
    assert expr.expr.right.value.value == "3"


def test_unary_minus_with_addition():
    # (-2) + 3
    expr = parse_expr("-2 + 3")

    assert expr.expr.op.value == "+"
    assert expr.expr.left.op.value == "-"
    assert expr.expr.left.right.value.value == "2"
    assert expr.expr.right.value.value == "3"
    
def test_empty_block():
    block = parse("fn test() {}")[0].body
    
    assert len(block.statements) == 0
    
def test_unexpected_token():
    with pytest.raises(
        ParserError,
        match=r"1:18: Unexpected token: End of file",
    ):
        parse_expr("5 + 2 -")