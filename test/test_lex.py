from lexer import *
import pytest


def lex(input: str):
    return Lexer(input).lex()


def token(type: TokenType, value: str):
    return Token(Location(0, 0), type, value)


def test_number():
    assert lex("425") == [
        token(TokenType.Number, "425"),
        token(TokenType.Eof, ""),
    ]


def test_whitespace():
    assert lex("   \t  \t\t") == [
        token(TokenType.Eof, ""),
    ]


def test_simple_expr():
    assert lex("1 + 2") == [
        token(TokenType.Number, "1"),
        token(TokenType.Plus, "+"),
        token(TokenType.Number, "2"),
        token(TokenType.Eof, ""),
    ]


def test_paren_expr():
    assert lex("(5 - 2) * 3") == [
        token(TokenType.LParen, "("),
        token(TokenType.Number, "5"),
        token(TokenType.Minus, "-"),
        token(TokenType.Number, "2"),
        token(TokenType.RParen, ")"),
        token(TokenType.Mul, "*"),
        token(TokenType.Number, "3"),
        token(TokenType.Eof, ""),
    ]


def test_unexpected_char():
    with pytest.raises(
        Exception,
        match=r"Unexpected character '@' at row 0, column 9",
    ):
        lex("74 + 1 * @")