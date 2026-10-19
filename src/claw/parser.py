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
    ReturnStmt,
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

RIGHT_ASSOCIATIVE = {}


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

    def parse_identifier(self) -> IdentifierExpr:
        token = self.consume_assert(
            TokenType.Identifier,
            "expected identifier",
        )
        start = token.location
        end = Location(start.row, start.column + len(token.value))
        return IdentifierExpr(Span(start, end), token)

    def peek(self, offset: int = 1) -> Token:
        index = self.cursor + offset
        if index < len(self.tokens):
            return self.tokens[index]
        return self.tokens[-1]

    def skip_newlines(self):
        while self.current._type is TokenType.Newline:
            self.consume()

    def parse(self) -> tuple[list[Statement], list[ParserError]]:
        statements = []

        while self.current._type is not TokenType.Eof:
            self.skip_newlines()
            if self.current._type is TokenType.Eof:
                break

            start = self.cursor

            try:
                statements.append(self.parse_top_level_statement())
            except ParserError as err:
                self.errors.append(err)
                self.synchronize_top_level()

            if start == self.cursor and self.current._type is not TokenType.Eof:
                self.consume()

        return statements, self.errors

    def synchronize_top_level(self):
        while self.current._type not in (
            TokenType.Eof,
            TokenType.Newline,
            TokenType.Fn,
            TokenType.Var,
        ):
            self.consume()

        self.skip_newlines()

    def parse_top_level_statement(self) -> Statement:
        if self.current._type is TokenType.Fn:
            return self.parse_function()

        match self.current._type:
            case TokenType.Var:
                start = self.consume().location
                name = self.parse_identifier()
                return VarDeclStmt(
                    Span(start, name.span.end),
                    name,
                )

            case _:
                raise ParserError(
                    Span(self.current.location, self.current.location),
                    "expected a declaration at the top level",
                )

    def parse_expression(self) -> Expression:
        left = self.parse_primary()

        while PRECEDENCE_MAP.get(self.current._type):
            op = self.consume()
            left = self.parse_binary_op(left, op)

        return left

    def parse_primary(self) -> Expression:
        match self.current._type:
            case TokenType.LParen:
                start = self.consume().location
                self.skip_newlines()
                expr = self.parse_expression()
                self.skip_newlines()

                if self.current._type is not TokenType.RParen:
                    raise ParserError(
                        Span(start, self.current.location),
                        "expected closing parenthesis",
                    )

                self.consume()
                return expr

            case TokenType.Number:
                token = self.consume()
                start = token.location
                end = Location(start.row, start.column + len(token.value))
                return NumberExpr(Span(start, end), token)

            case TokenType.Identifier:
                ident = self.parse_identifier()

                if self.current._type is not TokenType.LParen:
                    return ident

                return self.parse_call(ident)

            case TokenType.Minus:
                return self.parse_unary()

            case _:
                raise ParserError(
                    Span(self.current.location, self.current.location),
                    f"unexpected token {self.current.value}",
                )

    def parse_statement(self) -> Statement:
        match self.current._type:
            case TokenType.If:
                return self.parse_if_statement()

            case TokenType.Return:
                return self.parse_return_statement()

            case TokenType.Identifier:
                if self.peek()._type is TokenType.Assign:
                    ident = self.parse_identifier()
                    self.consume()  # assignment operator
                    expr = self.parse_expression()

                    return ExprStmt(
                        Span(ident.span.start, expr.span.end),
                        AssignExpr(
                            Span(ident.span.start, expr.span.end),
                            ident,
                            expr,
                        ),
                    )

                expr = self.parse_expression()
                return ExprStmt(expr.span, expr)

            case TokenType.LCurly:
                return self.parse_block()

            case _:
                expr = self.parse_expression()
                return ExprStmt(expr.span, expr)

    def parse_return_statement(self) -> ReturnStmt:
        token = self.consume()
        start = token.location
        end = Location(start.row, start.column + len(token.value))

        if self.current._type in (
            TokenType.Newline,
            TokenType.RCurly,
            TokenType.Eof,
        ):
            return ReturnStmt(Span(start, end))

        expr = self.parse_expression()
        return ReturnStmt(Span(start, expr.span.end), expr)

    def parse_if_statement(self) -> IfStmt:
        start = self.consume().location
        condition = self.parse_expression()

        self.skip_newlines()
        then_expr = self.parse_statement()
        self.skip_newlines()

        else_expr = None
        if self.current._type is TokenType.Else:
            self.consume()
            else_expr = self.parse_statement()

        end = else_expr.span.end if else_expr else then_expr.span.end
        return IfStmt(Span(start, end), condition, then_expr, else_expr)

    def parse_call(self, ident: IdentifierExpr) -> CallExpr:
        self.consume()  # opening parenthesis
        self.skip_newlines()
        arguments: list[Expression] = []

        while self.current._type not in (TokenType.RParen, TokenType.Eof):
            arguments.append(self.parse_expression())
            self.skip_newlines()

            if self.current._type is TokenType.Comma:
                self.consume()
                self.skip_newlines()
            elif self.current._type is not TokenType.RParen:
                raise ParserError(
                    Span(self.current.location, self.current.location),
                    "expected comma between function arguments",
                )

        start = ident.span.start
        end = self.consume_assert(
            TokenType.RParen,
            "expected closing parenthesis after function arguments",
        ).location

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

        while self.current._type not in (TokenType.RCurly, TokenType.Eof):
            self.skip_newlines()
            if self.current._type in (TokenType.RCurly, TokenType.Eof):
                break
            statements.append(self.parse_statement())

        end = self.consume_assert(
            TokenType.RCurly,
            "expected closing brace before end of file",
        ).location

        return Block(Span(start, end), statements)

    def parse_function(self) -> Function:
        start = self.consume().location
        name = self.parse_identifier()

        self.consume_assert(
            TokenType.LParen,
            "expected opening parenthesis after function name",
        )

        self.skip_newlines()
        parameters: list[IdentifierExpr] = []

        if self.current._type is not TokenType.RParen:
            while True:
                parameters.append(self.parse_identifier())
                self.skip_newlines()

                if self.current._type is TokenType.RParen:
                    break

                if self.current._type is not TokenType.Comma:
                    raise ParserError(
                        Span(self.current.location, self.current.location),
                        "expected comma after parameter",
                    )

                self.consume()
                self.skip_newlines()

        self.consume_assert(
            TokenType.RParen,
            "expected closing parenthesis after parameters",
        )

        self.skip_newlines()
        body = self.parse_statement()

        return Function(
            Span(start, body.span.end),
            name,
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
                    "left side of assignment must be an identifier",
                )

            return AssignExpr(Span(left.span.start, right.span.end), left, right)

        return BinaryOp(Span(left.span.start, right.span.end), left, op, right)