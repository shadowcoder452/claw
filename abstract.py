from lexer import Token, TokenType

class Expression:
    pass

class NumberExpr(Expression):
    def __init__(self, value: Token):
        self.value = value
        
class BinaryOp(Expression):
    def __init__(self, lhs: Expression, op: Token, rhs: Expression):
        self.lhs = lhs
        self.op = op
        self.rhs = rhs