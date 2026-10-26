from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING
from .lexer import Token
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
class Number(Expression):
    value: Token


@dataclass
class BinaryOp(Expression):
    left: Expression
    op: Token
    right: Expression


@dataclass
class Identifier(Expression):
    value: Token


@dataclass
class Call(Expression):
    callee: Identifier
    arguments: ExpressionList

@dataclass
class Assign(Expression):
    target: Identifier
    value: Expression

@dataclass
class If(Statement):
    condition: Expression
    then_expr: Statement
    else_expr: Statement | None


@dataclass
class Function(Statement):
    name: Identifier
    parameters: IdentifierList
    body: Statement
    
@dataclass
class WhenFlagClicked(Statement):
    body: Statement
    

@dataclass
class Block(Statement):
    statements: StatementList
    
@dataclass
class VarDecl(Statement):
    name: Identifier

@dataclass
class Return(Statement):
    expr: Expression | None = field(default=None)