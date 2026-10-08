from lexer import *
from parser import *
from semantic_analyzer import *
from pprint import pprint
from format_function import format_function
import sys
"""
fn add(a, b)
    a + b

fn function1()
    x = add(3, 2)
"""
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Expected exactly 1 argument, main <file>")
        sys.exit(1)
    
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
    
    for fn in ast:
        print(format_function(fn))