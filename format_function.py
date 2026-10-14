from abstract import *

def format_function(function: Function, indent: int = 0) -> str:
    prefix = " " * indent

    params = ", ".join(param.value for param in function.parameters)

    result = f"{prefix}fn {function.name}({params})"

    if function.body is not None:
        result += "\n" + format_expression(function.body, indent + 2)

    return result


def format_expression(expr: Expression, indent: int = 0) -> str:
    prefix = " " * indent

    if isinstance(expr, NumberExpr):
        return f"{prefix}Number: {expr.value.value}"

    if isinstance(expr, IdentifierExpr):
        return f"{prefix}Identifier: {expr.value.value}"

    if isinstance(expr, BinaryOp):
        return (
            f"{prefix}BinaryOp: {expr.op.value}\n"
            f"{format_expression(expr.left, indent + 2)}\n"
            f"{format_expression(expr.right, indent + 2)}"
        )

    if isinstance(expr, CallExpr):
        result = f"{prefix}Call: {expr.callee.value.value}"

        for argument in expr.arguments:
            result += "\n" + format_expression(argument, indent + 2)

        return result

    if isinstance(expr, IfStmt):
        result = f"{prefix}If\n"
        result += f"{prefix}  Condition:\n"
        result += format_expression(expr.condition, indent + 4)
        result += f"\n{prefix}  Then:\n"
        result += format_expression(expr.then_expr, indent + 4)

        if expr.else_expr is not None:
            result += f"\n{prefix}  Else:\n"
            result += format_expression(expr.else_expr, indent + 4)

        return result
    
    if isinstance(expr, AssignExpr):
        return (
            f"{prefix}AssignExpr\n"
            f"{format_expression(expr.target, indent + 2)}\n"
            f"{format_expression(expr.value, indent + 2)}"
        )

    return f"{prefix}Unknown expression: {type(expr).__name__}"