from lexer import Token, TokenType
from error_types import ParserError
from abstract import *

# Operator precedence - higher number = higher precedence
PRECEDENCE_MAP = {
    TokenType.Less: 100,
    TokenType.Greater: 100,
    TokenType.Equal: 100,
    TokenType.Plus: 200,
    TokenType.Minus: 200,
    TokenType.Mul: 400,
    TokenType.Div: 400,
}

RIGHT_ASSOCIATIVE = {
}

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
    
    def consume_assert(self, expected: TokenType, error_message: str) -> Token:
        token = self.consume()
        if token._type != expected:
            raise ParserError(Span(token.location, token.location), error_message)
        return token
    
    def parse(self) -> list[Function]:
        """Parse the entire program."""
        functions = []

        while self.current._type != TokenType.Eof:
            if self.current._type == TokenType.Fn:
                functions.append(self.parse_function())
            else:
                raise ParserError(
                    Span(self.current.location, self.current.location),
                    "Top-level expressions are not allowed"
                )

        return functions
    
    def parse_expression(self) -> Expression:
        left = self.parse_primary()

        while PRECEDENCE_MAP.get(self.current._type):
            op = self.consume()
            left = self.parse_binary_op(left, op)

        return left
    
    def parse_primary(self) -> Expression:
        match self.current._type:
            case TokenType.LParen:
                start = self.consume()
                expr = self.parse_expression()
                if self.current._type != TokenType.RParen:
                    raise ParserError(Span(start, self.current.location), f"Expected ')' but got {self.current._type}")
                self.consume()
                return expr
            
            case TokenType.Number:
                token = self.consume()
                return NumberExpr(Span(token.location, token.location), token)
            
            case TokenType.Identifier:
                token = self.consume()
                ident = IdentifierExpr(Span(token.location, token.location), token)
                
                if self.current._type != TokenType.LParen:
                    return ident
                
                self.consume()
                arguments: list[Expression] = []
                
                while self.current._type != TokenType.RParen and self.current._type != TokenType.Eof:
                    arguments.append(self.parse_expression())
                    if self.current._type == TokenType.Comma:
                        self.consume()
                
                self.consume_assert(TokenType.RParen, "Expected ')' after function arguments")
                return CallExpr(ident.span, ident, arguments)
            
            case TokenType.If:
                start = self.consume().location
                
                condition = self.parse_expression()
                then_expr = self.parse_expression()
                else_expr = None
                
                if self.current._type == TokenType.Else:
                    self.consume()
                    else_expr = self.parse_expression()
                
                end = else_expr.span.end if else_expr else then_expr.span.end
                
                return IfStmt(Span(start, end), condition, then_expr, else_expr)
            
            case TokenType.Minus:
                return self.parse_unary()
            
            case _:
                raise ParserError(
                    Span(self.current.location, self.current.location),
                    f"Unexpected token: {self.current._type.name}"
                )

    def parse_unary(self) -> Expression:
        if self.current._type != TokenType.Minus:
            return self.parse_primary()
        
        start = self.consume().location
        expr = self.parse_unary()
        return BinaryOp(
            Span(start, expr.span.end),
            NumberExpr(Span(start, start), Token(TokenType.Number, "0", start)),
            Token(TokenType.Minus, "-", start),
            expr,
        )
            
    def parse_function(self, is_extern: bool = False) -> Function:
        start = self.consume().location
        name = self.consume_assert(TokenType.Identifier, "Expected function name")
        self.consume_assert(TokenType.LParen, "Expected '(' after function name")

        # Parse parameters
        parameters: list[Token] = []

        if self.current._type != TokenType.RParen:
            while True:
                param = self.consume_assert(
                    TokenType.Identifier,
                    "Expected parameter name"
                )
                parameters.append(param)

                if self.current._type == TokenType.RParen:
                    break

                if self.current._type != TokenType.Comma:
                    raise ParserError(
                        Span(self.current.location, self.current.location),
                        "Expected ',' after parameter"
                    )

                self.consume()

        self.consume_assert(TokenType.RParen, "Expected ')' after parameters")
        
        body = self.parse_expression()
        end = body.span.end
        
        return Function(
            Span(start, end),
            name.value,
            parameters,
            body,
        )
        
    def parse_binary_op(self, left: Expression, op: Token) -> Expression:
        current_precedence = PRECEDENCE_MAP.get(op._type, 0)

        right = self.parse_primary()

        while True:
            next_precedence = PRECEDENCE_MAP.get(self.current._type, 0)

            if op._type in RIGHT_ASSOCIATIVE:
                if next_precedence < current_precedence:
                    break
            else:
                if next_precedence <= current_precedence:
                    break

            next_op = self.consume()
            right = self.parse_binary_op(right, next_op)

        if op._type == TokenType.Assign:
            if not isinstance(left, IdentifierExpr):
                raise ParserError(
                    left.span,
                    "Left side of assignment must be an identifier"
                )

            return AssignExpr(Span(left.span.start, right.span.end), left, right)

        return BinaryOp(Span(left.span.start, right.span.end), left, op, right)