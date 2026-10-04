from lexer import *
from parser import *

if __name__ == "__main__":

    # Test operator precedence: 2 + 3 * 4
    source = "2 + 3 * 4"
    lexer = Lexer(source)
    tokens = lexer.lex()
    parser = Parser(tokens)
    ast = parser.parse_expression()

    print(f"Expression: {source}")
    print(f"Root: {ast.op.value}")
    print(f"  Left: {ast.left.value.value}")
    print(f"  Right: BinaryOp {ast.right.op.value}")
    print(f"    Left: {ast.right.left.value.value}")
    print(f"    Right: {ast.right.right.value.value}")