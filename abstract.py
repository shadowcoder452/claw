from lexer import Token, TokenType

@dataclass
class Span:
    start: Location
    end: Location

class Expression:
    def __init__(self, span: Span):
        self.span = span

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
        
class Function:
    def __init__(
        self,
        name: str,
        parameters: list[Token],
        body: Expression | None,
    ):
        self.name = name
        self.parameters = parameters
        self.body = body  # None for extern functions