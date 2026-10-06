from location import Span

class Error(Exception):
    def __init__(self, span: Span, cause: str):
        self.span = span
        self.cause = cause
        
    def __str__(self):
        return f"{self.span.start.row + 1}:{self.span.start.column + 1}: {self.cause}"
    
class LexerError(Error): pass
class ParserError(Error): pass
class SemanticError(Error): pass

class SemanticWarning:
    def __init__(self, span: Span, cause: str):
        self.span = span
        self.cause = cause
        
    def __str__(self):
        return f"{self.span.start.row + 1}:{self.span.start.column + 1}: {self.cause}"