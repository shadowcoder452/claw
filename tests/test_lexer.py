from lexer import *
from error_types import *
import pytest


def lex(src: str):
    return Lexer(src).lex()

def test_number():
    assert lex("425") == [
        Token(TokenType.Number, "425"),
        Token(TokenType.Eof, "End of file"),
    ]


def test_whitespace():
    assert lex("   \t  \t\t") == [
        Token(TokenType.Eof, "End of file"),
    ]


def test_simple_expr():
    assert lex("1 + 2") == [
        Token(TokenType.Number, "1"),
        Token(TokenType.Plus, "+"),
        Token(TokenType.Number, "2"),
        Token(TokenType.Eof, "End of file"),
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
        Token(TokenType.Eof, "End of file"),
    ]
    
def test_identifier():
    assert lex("abcd") == [
        Token(TokenType.Identifier, "abcd"),
        Token(TokenType.Eof, "End of file"),
    ]
    
def test_semicolon():
    assert lex(";;\n;;;") == [
        Token(TokenType.Eof, "End of file")
    ]

def test_assignment():
    assert lex("x = 10") == [
        Token(TokenType.Identifier, "x"),
        Token(TokenType.Assign, "="),
        Token(TokenType.Number, "10"),
        Token(TokenType.Eof, "End of file"),
    ]
    
def test_single_char_token():
    assert lex("<") == [
        Token(TokenType.Less, "<"),
        Token(TokenType.Eof, "End of file"),
    ]
    
def test_paren_expr_comparison():
    assert lex("0 < (2 == 0);") == [
        Token(TokenType.Number, "0"),
        Token(TokenType.Less, "<"),
        Token(TokenType.LParen, "("),
        Token(TokenType.Number, "2"),
        Token(TokenType.Equal, "=="),
        Token(TokenType.Number, "0"),
        Token(TokenType.RParen, ")"),
        Token(TokenType.Eof, "End of file"),
    ]

def test_comment():
    assert lex("// test comment\n <") == [
        Token(TokenType.Less, "<"),
        Token(TokenType.Eof, "End of file"),
    ]

def test_unexpected_char():
    with pytest.raises(
        LexerError,
        match=r"1:10: Unexpected character '@'",
    ):
        lex("74 + 1 * @")