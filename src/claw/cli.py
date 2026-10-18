from .lexer import Lexer
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from pprint import pprint
from .ast_formatter import format_ast
from .errors import display_error
import sys

def main() -> int:
    if len(sys.argv) != 2:
        print("expected one file path")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens, errors = lexer.lex()
        
        if errors:
            for err in errors:
                display_error(err, source)
            return 1
        
        parser = Parser(tokens)
        ast, errors = parser.parse()
        
        if errors:
            for err in errors:
                display_error(err, source)
            return 2
        
        analyzer = SemanticAnalyzer(ast)
        errors = analyzer.analyze() 

        if errors:
            for err in errors:
                display_error(err, source)
            return 3
            
        print(format_ast(ast))
        return 0
    
    except FileNotFoundError:
        print("file not found")