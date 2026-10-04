from lexer import Token, TokenType

class Expression:
    pass

class NumberExpr(Expression):
    def __init__(self, value: Token):
        self.value = value
        
class BinaryOp(Expression):
    def __init__(self, left: Expression, op: Token, right: Expression):
        self.left = left
        self.op = op
        self.right = right