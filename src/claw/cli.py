from .lexer import Lexer
from .parser import Parser
from .semantic_analyzer import SemanticAnalyzer
from pprint import pprint
from .ast_formatter import format_ast
import sys

def main():
    if len(sys.argv) != 2:
        print("Expected exactly 1 argument, main <file>")
        sys.exit(1)
    
    try:
        with open(sys.argv[1], 'r') as f:
            source = f.read()
        
        lexer = Lexer(source)
        tokens = lexer.lex()
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer(ast)
        analyzer.analyze()
        
        for warning in analyzer.warnings:
            print(warning)
            
        print(format_ast(ast))
    except FileNotFoundError:
        print("File not found")