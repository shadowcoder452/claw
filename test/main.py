from lexer import *
from parser import *
from semantic_analyzer import *
from pprint import pprint
from format_function import format_function

if __name__ == "__main__":
    source = """
# Test the full parser

fn add(a, b)
    a + b

fn function1()
    x = add(3, 2)

    """

    lexer = Lexer(source)
    tokens = lexer.lex()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer(ast)
    analyzer.analyze()
    
    for fn in ast:
        print(format_function(fn))