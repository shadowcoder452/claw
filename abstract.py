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
        
class IdentifierExpr(Expression):
    def __init__(self, value: Token):
        self.value = value
        
class CallExpr(Expression):
    def __init__(self, callee: IdentifierExpr, arguments: list[Expression]):
        self.callee = callee
        self.arguments = arguments
        
class IfExpr(Expression):
    def __init__(
        self,
        condition: Expression,
        then_expr: Expression,
        else_expr: Expression | None,
    ):
        self.condition = condition
        self.then_expr = then_expr
        self.else_expr = else_expr  # None if no else clause