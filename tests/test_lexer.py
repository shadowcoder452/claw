import pytest

from claw.errors import LexerError
from claw.lexer import Lexer, Token, TokenType
from claw.location import Location, Span


def lex(source: str):
    return Lexer(source).lex()


def token(token_type: TokenType, value: str) -> Token:
    return Token(token_type, value)


def test_number():
    tokens, errors = lex("425")
    assert tokens == [
        token(TokenType.Number, "425"),
        token(TokenType.Eof, "End of file"),
    ]
    assert errors == []


def test_whitespace_only_source():
    tokens, errors = lex("   \t  \t\t")
    assert tokens == [token(TokenType.Eof, "End of file")]
    assert errors == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "1 + 2",
            [
                (TokenType.Number, "1"),
                (TokenType.Plus, "+"),
                (TokenType.Number, "2"),
            ],
        ),
        (
            "(5 - 2) * 3",
            [
                (TokenType.LParen, "("),
                (TokenType.Number, "5"),
                (TokenType.Minus, "-"),
                (TokenType.Number, "2"),
                (TokenType.RParen, ")"),
                (TokenType.Mul, "*"),
                (TokenType.Number, "3"),
            ],
        ),
        (
            "x = 10",
            [
                (TokenType.Identifier, "x"),
                (TokenType.Assign, "="),
                (TokenType.Number, "10"),
            ],
        ),
        (
            "0 < (2 == 0)",
            [
                (TokenType.Number, "0"),
                (TokenType.Less, "<"),
                (TokenType.LParen, "("),
                (TokenType.Number, "2"),
                (TokenType.Equal, "=="),
                (TokenType.Number, "0"),
                (TokenType.RParen, ")"),
            ],
        ),
    ],
)
def test_tokenizes_expressions(source, expected):
    tokens, errors = lex(source)
    assert tokens == [*(token(kind, value) for kind, value in expected), token(TokenType.Eof, "End of file")]
    assert errors == []


def test_identifier():
    tokens, errors = lex("abcd")
    assert tokens == [
        token(TokenType.Identifier, "abcd"),
        token(TokenType.Eof, "End of file"),
    ]
    assert errors == []

def test_keyword():
    tokens, errors = lex("return")
    assert tokens == [
        token(TokenType.Return, "return"),
        token(TokenType.Eof, "End of file"),
    ]
    assert errors == []



def test_semicolons_emit_newlines():
    tokens, errors = lex(";;;;;")
    assert tokens == [*(token(TokenType.Newline, ";") for _ in range(5)),token(TokenType.Eof, "End of file")]
    assert errors == []


def test_single_character_token():
    tokens, errors = lex("<")
    assert tokens == [
        token(TokenType.Less, "<"),
        token(TokenType.Eof, "End of file"),
    ]
    assert errors == []


def test_line_comment_is_ignored():
    tokens, errors = lex("// test comment\n <")
    assert tokens == [
        token(TokenType.Less, "<"),
        token(TokenType.Eof, "End of file"),
    ]
    assert errors == []


def test_unexpected_character_is_reported_and_lexing_continues():
    tokens, errors = lex("~ <")
    assert tokens == [
        token(TokenType.Less, "<"),
        token(TokenType.Eof, "End of file"),
    ]
    assert errors == [
        LexerError(Span(Location(0, 0), Location(0, 0)), "unexpected character"),
    ]


def test_invalid_number_literal_is_reported_without_emitting_a_number():
    tokens, errors = lex("123b")
    assert tokens == [token(TokenType.Eof, "End of file")]
    assert errors == [
        LexerError(Span(Location(0, 0), Location(0, 4)), "invalid number literal"),
    ]