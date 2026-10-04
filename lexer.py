from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Optional
from location import Location

class TokenType(Enum):
    # Literals
    Number = auto()
    Identifier = auto()

    # Keywords
    Fn = auto()       # Function
    If = auto()
    Else = auto()
    Extern = auto()
    
    LParen = auto()
    RParen = auto()
    Comma = auto()
    Colon = auto()

    # Operators
    Plus = auto()
    Minus = auto()
    Mul = auto()
    Div = auto()
    Less = auto()     # Comparison
    Greater = auto()  # Comparison
    Equal = auto()    # Equality (==)
    
    Eof = auto()
    
SINGLE_CHAR_TOKENS = {
    '(': TokenType.LParen,
    ')': TokenType.RParen,
    '+': TokenType.Plus,
    '-': TokenType.Minus,
    '*': TokenType.Mul,
    '/': TokenType.Div,
    '<': TokenType.Less,
    '>': TokenType.Greater,
    ',': TokenType.Comma,
    ':': TokenType.Colon,
}

KEYWORDS = {
    "fn": TokenType.Fn,
    "if": TokenType.If,
    "else": TokenType.Else,
    "extern": TokenType.Extern,
}

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
        return '\0'
    
    def peek(self, offset: int = 1) -> str:
        pos = self.cursor + offset
        if pos < len(self.source):
            return self.source[pos]
        return '\0'

    def increment(self):
        if self.current == '\n' or self.current == ';':
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
            
            if self.current == '#':
                while self.current != '\n' and self.current != '\0':
                    self.increment()
                continue
            
            # recognize numbers
            if self.current.isdigit():
                start = self.cursor
                while self.current.isdigit():
                    self.increment()
                
                self.push_token(TokenType.Number, self.source[start:self.cursor])
                continue
            
            # Check for == before single characters
            if self.current == '=' and self.peek() == '=':
                self.push_token(TokenType.Equal, "==")
                self.increment()
                self.increment()
                continue
            
            # recognize operators and parentheses
            if token_type := SINGLE_CHAR_TOKENS.get(self.current):
                self.push_token(token_type, self.current)
                self.increment()
                continue
            
            # recognize identifiers
            if self.current.isalpha() or self.current == '_':
                start = self.cursor
                while self.current.isalnum() or self.current == '_':
                    self.increment()
                    
                word = self.source[start:self.cursor]
                
                token_type = KEYWORDS.get(word, TokenType.Identifier)
                    
                self.push_token(token_type, word)
                continue

            raise Exception(f"Unexpected character '{self.current}' at row {self.row}, column {self.column}")

        # add EOF token
        self.tokens.append(Token(TokenType.Eof, "", Location(self.row, self.column)))
        return self.tokens