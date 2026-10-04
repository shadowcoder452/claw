from lexer import Token, TokenType
from dataclasses import dataclass
from location import Span

class Expression:
    def __init__(self, span: Span):
        self.span = span


class NumberExpr(Expression):
    def __init__(self, span: Span, value: Token):
        super().__init__(span)
        self.value = value


class BinaryOp(Expression):
    def __init__(
        self,
        span: Span,
        left: Expression,
        op: Token,
        right: Expression,
    ):
        super().__init__(span)
        self.left = left
        self.op = op
        self.right = right


class IdentifierExpr(Expression):
    def __init__(self, span: Span, value: Token):
        super().__init__(span)
        self.value = value


class CallExpr(Expression):
    def __init__(
        self,
        span: Span,
        callee: IdentifierExpr,
        arguments: list[Expression],
    ):
        super().__init__(span)
        self.callee = callee
        self.arguments = arguments


class IfExpr(Expression):
    def __init__(
        self,
        span: Span,
        condition: Expression,
        then_expr: Expression,
        else_expr: Expression | None,
    ):
        super().__init__(span)
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr


class Function(Expression):
    def __init__(
        self,
        span: Span,
        name: str,
        parameters: list[Token],
        body: Expression | None,
    ):
        super().__init__(span)
        self.name = name
        self.parameters = parameters
        self.body = body