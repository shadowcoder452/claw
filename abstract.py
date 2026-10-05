from dataclasses import dataclass
from lexer import Token, TokenType
from location import Span


@dataclass
class Expression:
    span: Span


@dataclass
class NumberExpr(Expression):
    value: Token


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: Token
    right: Expression


@dataclass
class IdentifierExpr(Expression):
    value: Token


@dataclass
class CallExpr(Expression):
    callee: IdentifierExpr
    arguments: list[Expression]


@dataclass
class IfExpr(Expression):
    condition: Expression
    then_expr: Expression
    else_expr: Expression | None


@dataclass
class Function(Expression):
    name: str
    parameters: list[Token]
    body: Expression | None
    
@dataclass
class VariableDeclExpr(Expression):
    name: str
    value: Expression | None
    
@dataclass
class VariableAssignExpr(Expression):
    name: str
    value: Expression