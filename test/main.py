

if __name__ == "__main__":
    # Manually build AST for: 2 + (3 * 4)
    ast = BinaryOp(
        left=NumberExpr(Token(TokenType.Number, "2")),
        op=Token(TokenType.Plus, "+"),
        right=BinaryOp(
            left=NumberExpr(Token(TokenType.Number, "3")),
            op=Token(TokenType.Mul, "*"),
            right=NumberExpr(Token(TokenType.Number, "4"))
        )
    )

    print("AST for: 2 + 3 * 4")
    print(f"Root operation: {ast.op.value}")
    print(f"  Left: {ast.left.value.value}")
    print(f"  Right operation: {ast.right.op.value}")
    print(f"    Left: {ast.right.left.value.value}")
    print(f"    Right: {ast.right.right.value.value}")