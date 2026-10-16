"""Public API for the Claw compiler package."""

from .errors import (
    Error,
    LexerError,
    ParserError,
    SemanticError,
    SemanticWarning,
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

__all__ = [
    "AssignExpr",
    "BinaryOp",
    "Block",
    "CallExpr",
    "Error",
    "ExprStmt",
    "Expression",
    "Function",
    "IdentifierExpr",
    "IfStmt",
    "Lexer",
    "LexerError",
    "NumberExpr",
    "Parser",
    "ParserError",
    "SemanticAnalyzer",
    "SemanticError",
    "SemanticWarning",
    "Statement",
    "Token",
    "TokenType",
    "VarDeclStmt",
    "display_error",
    "format_ast",
    "format_node",
]