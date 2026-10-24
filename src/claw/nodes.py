from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .lexer import Token, TokenType
from .location import Span

if TYPE_CHECKING:
    from .types import ExpressionList, IdentifierList, StatementList

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
    arguments: ExpressionList

@dataclass
class AssignExpr(Expression):
    target: IdentifierExpr
    value: Expression

@dataclass
class IfStmt(Statement):
    condition: Expression
    then_expr: Statement
    else_expr: Statement | None


@dataclass
class Function(Statement):
    name: IdentifierExpr
    parameters: IdentifierList
    body: Statement
    
@dataclass
class Block(Statement):
    statements: StatementList
    
@dataclass
class VarDeclStmt(Statement):
    name: IdentifierExpr

@dataclass
class ReturnStmt(Statement):
    expr: Expression | None = field(default=None)