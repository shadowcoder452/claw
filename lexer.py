from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional

class TokenType(Enum):
    Number = auto()
    Plus = auto()
    Minus = auto()
    Mul = auto()
    Div = auto()
    LParen = auto()
    RParen = auto()
    Eof = auto()
    
@dataclass
class Location:
    row: int
    column: int

@dataclass
class Token:
    _type: TokenType
    value: str
    location: Optional[Location] = field(compare=False, default=None)
    
class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.cursor = 0
        self.row = 0
        self.column = 0
        
    @property
    def current(self) -> str:
        if 0 <= self.cursor < len(self.source):
            return self.source[self.cursor]
        return "\0"

    def increment(self):
        if self.current == '\n':
            self.row += 1
            self.column = 0
        else:
            self.column += 1
        self.cursor += 1

    def push_token(self, token_type: TokenType, value: str):
        token = Token(
            token_type,
            value,
            Location(self.row, self.column - len(value) + 1),
        )
        self.tokens.append(token)
    
    def lex(self) -> list[Token]:
        self.tokens.clear()
        
        while self.current != '\0':
            # skip whitespace
            if self.current.isspace():
                self.increment()
                continue
            
            # recognize numbers
            if self.current.isdigit():
                start = self.cursor
                while self.current.isdigit():
                    self.increment()
                
                self.push_token(TokenType.Number, self.source[start:self.cursor])
                continue
            
            # recognize operators and parentheses
            single_char_tokens = {
                '(': TokenType.LParen,
                ')': TokenType.RParen,
                '+': TokenType.Plus,
                '-': TokenType.Minus,
                '*': TokenType.Mul,
                '/': TokenType.Div,
            }

            if token_type := single_char_tokens.get(self.current):
                self.push_token(token_type, self.current)
                self.increment()
                continue

            raise Exception(f"Unexpected character '{self.current}' at row {self.row}, column {self.column}")

        # add EOF token
        self.tokens.append(Token(TokenType.Eof, "", Location(self.row, self.column)))
        return self.tokens