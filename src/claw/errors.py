from .location import Span
from dataclasses import dataclass
from ._ansi import BOLD, YELLOW, RED, RESET

@dataclass
class Error(Exception):
    span: Span
    cause: str
    
    def __post_init__(self):
        Exception.__init__(self, self.cause)
        
    def __str__(self):
        return f"{BOLD}{RED}error:{RESET} {self.span.start.row + 1}:{self.span.start.column + 1}: {self.cause}"
    
class LexerError(Error): pass
class ParserError(Error): pass
class SemanticError(Error): pass

class SemanticWarning(Error):
    def __str__(self):
        return f"{YELLOW}warning:{RESET} {self.span.start.row + 1}:{self.span.start.column + 1}: {self.cause}"

def display_error(error: Error, src: str):
    lines = src.splitlines()
    start = error.span.start
    end = error.span.end

    print(error)

    if start.row >= len(lines):
        return

    for row in range(start.row, min(end.row + 1, len(lines))):
        line = lines[row]
        line_num = row + 1
        padding = len(str(line_num))

        print(f"{YELLOW}{line_num:>{padding}} |{RESET} {line}")

        if row == start.row:
            underline_start = start.column
        else:
            underline_start = 0

        if row == end.row:
            underline_end = end.column
        else:
            underline_end = len(line)

        length = max(1, underline_end - underline_start)

        print(
            f"{' ' * padding} | "
            f"{' ' * underline_start}"
            f"{RED}^{'~' * (length - 1)}{RESET}"
        )