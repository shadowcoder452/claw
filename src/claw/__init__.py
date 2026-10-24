"""Public API for the Claw compiler package."""

from . import types
from .errors import (
    Error,
    LexerError,
    ParserError,
    SemanticError,
    display_error,
)
from .lexer import Lexer, Token, TokenType
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
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from .ast_formatter import format_ast, format_node
from .types import (
    ExpressionList,
    IdentifierList,
    LexResult,
    ParseResult,
    Program,
    StatementList,
    TokenStream,
)

__all__ = [
    "AssignExpr",
    "BinaryOp",
    "Block",
    "CallExpr",
    "Error",
    "ExprStmt",
    "ExpressionList",
    "Expression",
    "Function",
    "IdentifierList",
    "IdentifierExpr",
    "IfStmt",
    "Lexer",
    "LexerError",
    "LexResult",
    "NumberExpr",
    "Parser",
    "ParserError",
    "ParseResult",
    "Program",
    "SemanticAnalyzer",
    "SemanticError",
    "Statement",
    "StatementList",
    "Token",
    "TokenStream",
    "TokenType",
    "VarDeclStmt",
    "display_error",
    "format_ast",
    "format_node",
    "types",
]