from lexer import *
from parser import *

if __name__ == "__main__":
    source = """
    # Test the full parser
    fn factorial(n)
        if n < 2
            1
        else
            n * factorial(n - 1)

    fn fib(n)
        if n < 2
            n
        else
            fib(n - 1) + fib(n - 2)

    # Top-level expression
    factorial(5)
    """

    lexer = Lexer(source)
    tokens = lexer.lex()
    parser = Parser(tokens)
    functions = parser.parse()