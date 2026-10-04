from lexer import Token, TokenType
from abstract import Expression, NumberExpr, BinaryOp

# Operator precedence - higher number = higher precedence
PRECEDENCE_MAP = {
    TokenType.Mul: 40,
    TokenType.Div: 40,
    TokenType.Plus: 20,
    TokenType.Minus: 20,
}

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.cursor = 0
        
    @property
    def current(self) -> Token:
        if 0 <= self.cursor < len(self.tokens):
            return self.tokens[self.cursor]
        return self.tokens[-1]
    
    def consume(self) -> Token:
        if 0 <= self.cursor < len(self.tokens):
            token = self.tokens[self.cursor]
        else:
            token = self.tokens[-1]
        self.cursor += 1
        return token
    
    def parse_expression(self) -> Expression:
        left = self.parse_primary()

        while PRECEDENCE_MAP.get(self.current._type):
            op = self.consume()
            left = self.parse_binary_op(left, op)

        return left
    
    def parse_primary(self) -> Expression:
        match self.current._type:
            case TokenType.LParen:
                self.consume()
                expr = self.parse_expression()
                if self.current._type != TokenType.RParen:
                    raise ParserError(f"Expected ')' but got {self.current._type}")
                self.consume()
                return expr
            
            case TokenType.Number:
                token = self.consume()
                return NumberExpr(token)
            
            case _:
                raise ParserError(f"Unexpected token: {self.current._type.name}")
            
    def parse_binary_op(self, left: Expression, op: Token) -> Expression:
        """Parse a binary operation using precedence climbing."""
        # Get the precedence of the current operator
        current_precedence = PRECEDENCE_MAP.get(op._type, 0)
        
        right = self.parse_primary()
        
        while PRECEDENCE_MAP.get(self.current._type, 0) > current_precedence:
            next_op = self.consume()
            right = self.parse_binary_op(right, next_op)
            
        return BinaryOp(left, op, right)