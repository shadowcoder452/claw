from .lexer import Token, TokenType
from .errors import ParserError
from .location import Span, Location
from .nodes import (
    AssignExpr,
    BinaryOp,
    Block,
    CallExpr,
    ExprStmt,
    Expression,
    Function,
    IdentifierExpr,
    IfStmt,
    NumberExpr,
    Statement,
    VarDeclStmt,
)

# Operator precedence - higher number = higher precedence
PRECEDENCE_MAP = {
    TokenType.Assign: 50,
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
        self.errors: list[ParserError] = []
        
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
        if token._type is not expected:
            raise ParserError(Span(token.location, token.location), error_message)
        return token
    
    def peek(self, offset: int = 1) -> Token:
        index = self.cursor + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return self.tokens[-1]
    
    def parse(self) -> tuple[list[Statement], list[ParserError]]:
        statements = []

        while self.current._type is not TokenType.Eof:
            start = self.cursor

            try:
                if self.current._type is TokenType.Fn:
                    statements.append(self.parse_function())
                else:
                    statements.append(self.parse_top_level())
            except ParserError as err:
                self.errors.append(err)
                self.synchronize_top_level()

            if start == self.cursor and self.current._type is not TokenType.Eof:
                self.consume()

        return statements, self.errors

    def synchronize_top_level(self):
        while self.current._type is not TokenType.Eof:
            if self.current._type in (TokenType.Fn, TokenType.Var):
                return
            self.consume()
    
    def parse_expression(self) -> Expression:
        left = self.parse_primary()

        while PRECEDENCE_MAP.get(self.current._type):
            op = self.consume()
            left = self.parse_binary_op(left, op)

        return left
    
    def parse_top_level(self) -> Statement:
        match self.current._type:
            case TokenType.Var:
                start = self.consume().location
                
                ident = self.consume_assert(TokenType.Identifier, f"expected identifier")
                ident_expr = IdentifierExpr(Span(start, self.current.location), ident)
                
                return VarDeclStmt(Span(start, self.current.location), ident_expr)
                
            case _:
                raise ParserError(
                    Span(self.current.location, self.current.location),
                    f"expected a declaration at the top level"
                )
    
    def parse_primary(self) -> Expression:
        match self.current._type:
            case TokenType.LParen:
                start = self.consume().location
                expr = self.parse_expression()
                if self.current._type is not TokenType.RParen:
                    raise ParserError(Span(start, self.current.location), f"expected closing parenthesis")
                self.consume()
                return expr
            
            case TokenType.Number:
                token = self.consume()
                start = token.location
                end = Location(start.row, start.column + len(token.value))
                return NumberExpr(Span(start, end), token)
            
            case TokenType.Identifier:
                token = self.consume()
                start = token.location
                end = Location(start.row, start.column + len(token.value))
                ident = IdentifierExpr(Span(start, end), token)
                
                if self.current._type is not TokenType.LParen:
                    return ident
                
                return self.parse_call(ident)
            
            case TokenType.Minus:
                return self.parse_unary()
            
            case _:
                raise ParserError(
                    Span(self.current.location, self.current.location),
                    f"unexpected token {self.current.value}"
                )
    
    def parse_statement(self) -> Statement:
        match self.current._type:
            case TokenType.If:
                return self.parse_if_statement()
            
            case TokenType.Identifier:
                if self.peek()._type is TokenType.Assign:
                    token = self.consume()
                    ident = IdentifierExpr(Span(token.location, self.current.location), token)

                    self.consume()
                    expr = self.parse_expression()

                    return ExprStmt(
                        Span(ident.span.start, expr.span.end),
                        AssignExpr(
                            Span(ident.span.start, expr.span.end),
                            ident,
                            expr
                        )
                    )

                return self.parse_expression()
            
            case TokenType.LCurly:
                return self.parse_block()
            
            case _:
                expr = self.parse_expression()
                return ExprStmt(expr.span, expr)
        
                
    def parse_if_statement(self) -> IfStmt:
        start = self.consume().location
        
        condition = self.parse_expression()
        then_expr = self.parse_statement()
        else_expr = None
        
        if self.current._type is TokenType.Else:
            self.consume()
            else_expr = self.parse_statement()
        
        end = else_expr.span.end if else_expr else then_expr.span.end
        
        return IfStmt(Span(start, end), condition, then_expr, else_expr)                
                
    def parse_call(self, ident: IdentifierExpr) -> CallExpr:
        self.consume()
        arguments: list[Expression] = []
        
        while self.current._type not in (
            TokenType.RParen,
            TokenType.Eof
        ):
            arguments.append(self.parse_expression())
            if self.current._type is TokenType.Comma:
                self.consume()
        
        start = ident.span.start
        end = self.consume_assert(TokenType.RParen, "expected closing parenthesis after function arguments").location
        
        return CallExpr(Span(start, end), ident, arguments)

    def parse_unary(self) -> Expression:
        if self.current._type is not TokenType.Minus:
            return self.parse_primary()
        
        start = self.consume().location
        expr = self.parse_unary()
        return BinaryOp(
            Span(start, expr.span.end),
            NumberExpr(Span(start, start), Token(TokenType.Number, "0", start)),
            Token(TokenType.Minus, "-", start),
            expr,
        )
        
    def parse_block(self) -> Block:
        start = self.consume().location

        statements = []

        while self.current._type not in (
            TokenType.RCurly,
            TokenType.Eof,
        ):
            statements.append(self.parse_statement())

        end = self.consume_assert(TokenType.RCurly, "expected closing brace before end of file").location

        return Block(
            Span(start, end),
            statements,
        )
            
    def parse_function(self) -> Function:
        start = self.consume().location
        name = self.consume_assert(TokenType.Identifier, "expected function name")
        self.consume_assert(TokenType.LParen, "expected opening parenthesis after function name")
        
        parameters: list[Token] = []

        if self.current._type is not TokenType.RParen:
            while True:
                param = self.consume_assert(
                    TokenType.Identifier,
                    "expected parameter name"
                )
                parameters.append(param)

                if self.current._type is TokenType.RParen:
                    break

                if self.current._type is not TokenType.Comma:
                    raise ParserError(
                        Span(self.current.location, self.current.location),
                        "expected comma after parameter"
                    )

                self.consume()

        self.consume_assert(TokenType.RParen, "expected closing parenthesis after parameters")
        
        body = self.parse_statement()
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

        if op._type is TokenType.Assign:
            if not isinstance(left, IdentifierExpr):
                raise ParserError(
                    left.span,
                    "left side of assignment must be an identifier"
                )
            
            return AssignExpr(Span(left.span.start, right.span.end), left, right)

        return BinaryOp(Span(left.span.start, right.span.end), left, op, right)