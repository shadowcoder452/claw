import pytest

from claw.errors import ParserError
from claw.lexer import Lexer
from claw.nodes import (
    AssignExpr,
    BinaryOp,
    Block,
    CallExpr,
    ExprStmt,
    Function,
    IdentifierExpr,
    IfStmt,
    NumberExpr,
    ReturnStmt,
)
from claw.parser import Parser


def parse(source: str):
    tokens, lexer_errors = Lexer(source).lex()
    assert not lexer_errors
    return Parser(tokens).parse()


def parse_expression(source: str):
    statements, errors = parse(f"fn test() {{\n{source}\n}}")
    assert not errors
    function = statements[0]
    assert isinstance(function, Function)
    assert isinstance(function.body, Block)
    statement = function.body.statements[0]
    return statement.expr if isinstance(statement, ExprStmt) else statement


def number_value(node):
    assert isinstance(node, NumberExpr)
    return node.value.value


def test_number_expression():
    assert number_value(parse_expression("42")) == "42"


def test_identifier_expression():
    expression = parse_expression("x")
    assert isinstance(expression, IdentifierExpr)
    assert expression.value.value == "x"


@pytest.mark.parametrize(
    ("source", "operator", "left", "right"),
    [
        ("2 + 3", "+", "2", "3"),
        ("5 - 2", "-", "5", "2"),
        ("4 * 3", "*", "4", "3"),
        ("8 / 2", "/", "8", "2"),
        ("2 < 3", "<", "2", "3"),
        ("3 > 2", ">", "3", "2"),
        ("2 == 2", "==", "2", "2"),
    ],
)
def test_binary_expression(source, operator, left, right):
    expression = parse_expression(source)
    assert isinstance(expression, BinaryOp)
    assert expression.op.value == operator
    assert number_value(expression.left) == left
    assert number_value(expression.right) == right


def test_parentheses_override_precedence():
    expression = parse_expression("(2 + 3) * 4")
    assert isinstance(expression, BinaryOp)
    assert expression.op.value == "*"
    assert expression.left.op.value == "+"
    assert number_value(expression.left.left) == "2"
    assert number_value(expression.left.right) == "3"
    assert number_value(expression.right) == "4"


def test_multiplication_has_higher_precedence_than_addition():
    expression = parse_expression("2 + 3 * 4")
    assert expression.op.value == "+"
    assert number_value(expression.left) == "2"
    assert expression.right.op.value == "*"
    assert number_value(expression.right.left) == "3"
    assert number_value(expression.right.right) == "4"


def test_addition_is_left_associative():
    expression = parse_expression("1 + 2 + 3")
    assert expression.op.value == "+"
    assert expression.left.op.value == "+"
    assert number_value(expression.left.left) == "1"
    assert number_value(expression.left.right) == "2"
    assert number_value(expression.right) == "3"


def test_function_call():
    expression = parse_expression("foo(42)")
    assert isinstance(expression, CallExpr)
    assert expression.callee.value.value == "foo"
    assert [number_value(arg) for arg in expression.arguments] == ["42"]


def test_function_call_with_multiple_expression_arguments():
    expression = parse_expression("foo(1 + 2, 3 * 4)")
    assert isinstance(expression, CallExpr)
    assert len(expression.arguments) == 2
    assert expression.arguments[0].op.value == "+"
    assert expression.arguments[1].op.value == "*"


def test_if_statement_with_optional_else():
    expression = parse_expression("if 1 < 2 3")
    assert isinstance(expression, IfStmt)
    assert expression.condition.op.value == "<"
    assert expression.then_expr.expr.value.value == "3"
    assert expression.else_expr is None


def test_if_else_statement():
    expression = parse_expression("if 1 < 2 3 else 4")
    assert isinstance(expression, IfStmt)
    assert expression.then_expr.expr.value.value == "3"
    assert expression.else_expr.expr.value.value == "4"


def test_function_with_parameters():
    statements, errors = parse("fn add(a, b) a + b")
    assert not errors
    function = statements[0]
    assert isinstance(function, Function)
    assert function.name.value.value == "add"
    assert [parameter.value.value for parameter in function.parameters] == ["a", "b"]
    assert function.body.expr.op.value == "+"
    assert function.body.expr.left.value.value == "a"
    assert function.body.expr.right.value.value == "b"


def test_function_without_parameters():
    statements, errors = parse("fn answer() 42")
    assert not errors
    function = statements[0]
    assert function.name.value.value == "answer"
    assert function.parameters == []
    assert number_value(function.body.expr) == "42"


def test_multiple_functions():
    statements, errors = parse("fn add(a, b) a + b\nfn sub(a, b) a - b")
    assert not errors
    assert [function.name.value.value for function in statements] == ["add", "sub"]


@pytest.mark.parametrize("source", ["-5", "-x", "-(2 + 3)", "--5"])
def test_unary_minus(source):
    expression = parse_expression(source)
    assert isinstance(expression, BinaryOp)
    assert expression.op.value == "-"
    assert number_value(expression.left) == "0"


def test_empty_block():
    statements, errors = parse("fn test() {}")
    assert not errors
    function = statements[0]
    assert isinstance(function.body, Block)
    assert function.body.statements == []

def test_return_statement():
    statements, errors = parse("fn test() return 42")
    assert not errors
    function = statements[0]
    assert isinstance(function.body, ReturnStmt)

def test_assignment_expression():
    expression = parse_expression("x = 42")
    assert isinstance(expression, AssignExpr)
    assert expression.target.value.value == "x"
    assert number_value(expression.value) == "42"


def test_parser_collects_syntax_errors():
    tokens, lexer_errors = Lexer("fn test() { 5 + 2 - }").lex()
    assert not lexer_errors

    statements, errors = Parser(tokens).parse()

    assert statements == []
    assert len(errors) == 1
    assert isinstance(errors[0], ParserError)
    assert "unexpected token" in errors[0].cause