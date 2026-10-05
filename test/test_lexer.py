from lexer import *
import pytest


def lex(input: str):
    return Lexer(input).lex()

def test_number():
    assert lex("425") == [
        Token(TokenType.Number, "425"),
        Token(TokenType.Eof, ""),
    ]


def test_whitespace():
    assert lex("   \t  \t\t") == [
        Token(TokenType.Eof, ""),
    ]


def test_simple_expr():
    assert lex("1 + 2") == [
        Token(TokenType.Number, "1"),
        Token(TokenType.Plus, "+"),
        Token(TokenType.Number, "2"),
        Token(TokenType.Eof, ""),
    ]


def test_paren_expr():
    assert lex("(5 - 2) * 3") == [
        Token(TokenType.LParen, "("),
        Token(TokenType.Number, "5"),
        Token(TokenType.Minus, "-"),
        Token(TokenType.Number, "2"),
        Token(TokenType.RParen, ")"),
        Token(TokenType.Mul, "*"),
        Token(TokenType.Number, "3"),
        Token(TokenType.Eof, ""),
    ]
    
def test_identifier():
    assert lex("abcd") == [
        Token(TokenType.Identifier, "abcd"),
        Token(TokenType.Eof, ""),
    ]
    
def test_semicolon():
    assert lex(";;\n;;;") == [
        Token(TokenType.Eof, "")
    ]

def test_assignment():
    assert lex("x = 10") == [
        Token(TokenType.Identifier, "x"),
        Token(TokenType.Assign, "="),
        Token(TokenType.Number, "10"),
        Token(TokenType.Eof, ""),
    ]

def test_unexpected_char():
    with pytest.raises(
        Exception,
        match=r"Unexpected character '@' at row 0, column 9",
    ):
        lex("74 + 1 * @")