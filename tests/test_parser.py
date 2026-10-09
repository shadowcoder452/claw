from lexer import *
from parser import *


def parse(source: str):
    lexer = Lexer(source)
    tokens = lexer.lex()
    parser = Parser(tokens)
    return parser.parse()


def parse_expr(source: str):
    return parse(f"fn test() {source}")


def test_number():
    ast = parse_expr("42")[0]

    assert ast.body.value.value == "42"


def test_identifier():
    ast = parse_expr("x")[0]

    assert ast.body.value.value == "x"


def test_addition():
    ast = parse_expr("2 + 3")[0]

    assert ast.body.op.value == "+"
    assert ast.body.left.value.value == "2"
    assert ast.body.right.value.value == "3"


def test_subtraction():
    ast = parse_expr("5 - 2")[0]

    assert ast.body.op.value == "-"
    assert ast.body.left.value.value == "5"
    assert ast.body.right.value.value == "2"


def test_multiplication():
    ast = parse_expr("4 * 3")[0]

    assert ast.body.op.value == "*"
    assert ast.body.left.value.value == "4"
    assert ast.body.right.value.value == "3"


def test_division():
    ast = parse_expr("8 / 2")[0]

    assert ast.body.op.value == "/"
    assert ast.body.left.value.value == "8"
    assert ast.body.right.value.value == "2"


def test_less_than():
    ast = parse_expr("2 < 3")[0]

    assert ast.body.op.value == "<"
    assert ast.body.left.value.value == "2"
    assert ast.body.right.value.value == "3"


def test_greater_than():
    ast = parse_expr("3 > 2")[0]

    assert ast.body.op.value == ">"
    assert ast.body.left.value.value == "3"
    assert ast.body.right.value.value == "2"


def test_equal():
    ast = parse_expr("2 == 2")[0]

    assert ast.body.op.value == "=="
    assert ast.body.left.value.value == "2"
    assert ast.body.right.value.value == "2"


def test_parentheses():
    ast = parse_expr("(2 + 3) * 4")[0]

    assert ast.body.op.value == "*"

    assert ast.body.left.op.value == "+"
    assert ast.body.left.left.value.value == "2"
    assert ast.body.left.right.value.value == "3"

    assert ast.body.right.value.value == "4"


def test_operator_precedence():
    # 2 + (3 * 4)
    ast = parse_expr("2 + 3 * 4")[0]

    assert ast.body.op.value == "+"
    assert ast.body.left.value.value == "2"

    assert ast.body.right.op.value == "*"
    assert ast.body.right.left.value.value == "3"
    assert ast.body.right.right.value.value == "4"


def test_operator_precedence_reversed():
    # (2 * 3) + 4
    ast = parse_expr("2 * 3 + 4")[0]

    assert ast.body.op.value == "+"

    assert ast.body.left.op.value == "*"
    assert ast.body.left.left.value.value == "2"
    assert ast.body.left.right.value.value == "3"

    assert ast.body.right.value.value == "4"


def test_multiple_operations():
    # (1 + (2 * 3)) + 4
    ast = parse_expr("1 + 2 * 3 + 4")[0]

    assert ast.body.op.value == "+"
    assert ast.body.left.op.value == "+"

    assert ast.body.left.left.value.value == "1"

    assert ast.body.left.right.op.value == "*"
    assert ast.body.left.right.left.value.value == "2"
    assert ast.body.left.right.right.value.value == "3"

    assert ast.body.right.value.value == "4"


def test_left_associativity():
    # (10 - 3) - 2, NOT 10 - (3 - 2)
    ast = parse_expr("10 - 3 - 2")[0]

    assert ast.body.op.value == "-"

    assert ast.body.left.op.value == "-"
    assert ast.body.left.left.value.value == "10"
    assert ast.body.left.right.value.value == "3"

    assert ast.body.right.value.value == "2"


def test_function_call():
    ast = parse_expr("foo(42)")[0]

    call = ast.body

    assert call.callee.value.value == "foo"
    assert len(call.arguments) == 1
    assert call.arguments[0].value.value == "42"


def test_function_call_multiple_arguments():
    ast = parse_expr("foo(1, 2, 3)")[0]

    call = ast.body

    assert call.callee.value.value == "foo"
    assert len(call.arguments) == 3

    assert call.arguments[0].value.value == "1"
    assert call.arguments[1].value.value == "2"
    assert call.arguments[2].value.value == "3"


def test_function_call_expression_arguments():
    ast = parse_expr("foo(1 + 2, 3 * 4)")[0]

    call = ast.body

    assert call.arguments[0].op.value == "+"
    assert call.arguments[0].left.value.value == "1"
    assert call.arguments[0].right.value.value == "2"

    assert call.arguments[1].op.value == "*"
    assert call.arguments[1].left.value.value == "3"
    assert call.arguments[1].right.value.value == "4"


def test_if_expression():
    ast = parse_expr("if 1 < 2 3")[0]

    if_expr = ast.body

    assert if_expr.condition.op.value == "<"
    assert if_expr.condition.left.value.value == "1"
    assert if_expr.condition.right.value.value == "2"

    assert if_expr.then_expr.value.value == "3"
    assert if_expr.else_expr is None


def test_if_else_expression():
    ast = parse_expr("if 1 < 2 3 else 4")[0]

    if_expr = ast.body

    assert if_expr.condition.op.value == "<"
    assert if_expr.then_expr.value.value == "3"
    assert if_expr.else_expr.value.value == "4"


def test_function():
    ast = parse("fn add(a, b) a + b")[0]

    function = ast

    assert function.name == "add"
    assert len(function.parameters) == 2

    assert function.parameters[0].value == "a"
    assert function.parameters[1].value == "b"

    assert function.body.op.value == "+"
    assert function.body.left.value.value == "a"
    assert function.body.right.value.value == "b"


def test_function_no_parameters():
    ast = parse("fn foo() 42")[0]

    function = ast

    assert function.name == "foo"
    assert function.parameters == []
    assert function.body.value.value == "42"


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