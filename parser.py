from lexer import Token, TokenType
from abstract import *

# Operator precedence - higher number = higher precedence
PRECEDENCE_MAP = {
    TokenType.Less: 10,
    TokenType.Greater: 10,
    TokenType.Equal: 10,
    TokenType.Plus: 20,
    TokenType.Minus: 20,
    TokenType.Mul: 40,
    TokenType.Div: 40,
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
    
    def consume_assert(self, expected: Token, error_message: str) -> Token:
        token = self.consume()
        if token != expected:
            raise Exception(error_message)
        return token
    
    def parse(self) -> list[Function]:
        """Parse the entire program."""
        functions = []

        while self.current._type != TokenType.Eof:
            if self.current._type == TokenType.Fn:
                functions.append(self.parse_function())
            elif self.current._type == TokenType.Extern:
                self.consume()  # eat 'extern'
                functions.append(self.parse_function(is_extern=True))
            else:
                # Top-level expression - wrap it in an anonymous function
                expr = self.parse_expression()
                func = Function(expr.span, f"__anon_{len(functions)}", [], expr)
                functions.append(func)

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
                self.consume()
                expr = self.parse_expression()
                if self.current._type != TokenType.RParen:
                    raise ParserError(f"Expected ')' but got {self.current._type}")
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
                return CallExpr(Span(ident.span.start, ident.span.end), ident, arguments)
            
            case TokenType.If:
                self.consume()
                
                condition = self.parse_expression()
                then_expr = self.parse_expression()
                else_expr = None
                
                if self.current._type == TokenType.Else:
                    self.consume()
                    else_expr = self.parse_expression()
                
                span = Span(condition.span.start, else_expr.span.end if else_expr else then_expr.span.end)
                return IfExpr(span, condition, then_expr, else_expr)
            
            case _:
                raise ParserError(f"Unexpected token: {self.current._type.name}")
            
    def parse_function(self, is_extern: bool = False) -> Function:
        start = self.consume().location

        name = self.consume_assert(TokenType.Identifier, "Expected function name")
        self.consume_assert(TokenType.LParen, "Expected '(' after function name")

        # Parse parameters
        parameters: list[Token] = []
        while self.current._type != TokenType.RParen and self.current._type != TokenType.Eof:
            param = self.consume_assert(TokenType.Identifier, "Expected parameter name")
            parameters.append(param)
            if self.current._type == TokenType.Comma:
                self.consume()

        self.consume_assert(TokenType.RParen, "Expected ')' after parameters")
        
        if is_extern:
            end = ...
            body = None
        else:
            body = self.parse_expression()
            end = body.span.end

        return Function(
            Span(start, body.span.end if body is not None else end),
            name.value,
            parameters,
            body,
        ) 
        
    def parse_binary_op(self, left: Expression, op: Token) -> Expression:
        """Parse a binary operation using precedence climbing."""
        
        # Get the precedence of the current operator
        current_precedence = PRECEDENCE_MAP.get(op._type, 0)
        
        right = self.parse_primary()
        
        while PRECEDENCE_MAP.get(self.current._type, 0) > current_precedence:
            next_op = self.consume()
            right = self.parse_binary_op(right, next_op)
            
        return BinaryOp(Span(left.span.start, right.span.end), left, op, right)