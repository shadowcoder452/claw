from .errors import LexerError, ParserError
from .lexer import Token
from .nodes import Expression, IdentifierExpr, Statement


type TokenStream = list[Token]
type ExpressionList = list[Expression]
type IdentifierList = list[IdentifierExpr]
type StatementList = list[Statement]
type Program = StatementList

type LexResult = tuple[TokenStream, list[LexerError]]
type ParseResult = tuple[Program, list[ParserError]]
