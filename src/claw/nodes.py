from dataclasses import dataclass, field
from .lexer import Token, TokenType
from .location import Span

@dataclass
class Expression:
    span: Span
    
@dataclass
class Statement:
    span: Span
    
@dataclass
class ExprStmt(Statement):
    expr: Expression


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
class AssignExpr(Expression):
    target: IdentifierExpr
    value: Expression

@dataclass
class IfStmt(Statement):
    condition: Statement
    then_expr: Statement
    else_expr: Statement | None


@dataclass
class Function(Statement):
    name: IdentifierExpr
    parameters: list[IdentifierExpr]
    body: Statement
    
@dataclass
class Block(Statement):
    statements: list[Statement]
    
@dataclass
class VarDeclStmt(Statement):
    name: IdentifierExpr

@dataclass
class ReturnStmt(Statement):
    expr: Expression | None = field(default=None)