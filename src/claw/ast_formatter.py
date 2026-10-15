from . import nodes


def format_node(node, indent: int = 0) -> str:
    prefix = " " * indent

    match node:
        case nodes.Function(name=name, parameters=parameters, body=body):
            params = ", ".join(param.value for param in parameters)
            return (
                f"{prefix}Function {name}({params})\n"
                f"{format_node(body, indent + 2)}"
            )

        case nodes.ExprStmt(expr=expr):
            return format_node(expr, indent)

        case nodes.NumberExpr(value=value):
            return f"{prefix}Number: {value.value}"

        case nodes.IdentifierExpr(value=value):
            return f"{prefix}Identifier: {value.value}"

        case nodes.BinaryOp(left=left, op=op, right=right):
            return (
                f"{prefix}BinaryOp: {op.value}\n"
                f"{format_node(left, indent + 2)}\n"
                f"{format_node(right, indent + 2)}"
            )

        case nodes.CallExpr(callee=callee, arguments=arguments):
            result = f"{prefix}Call: {callee.value.value}"
            for argument in arguments:
                result += f"\n{format_node(argument, indent + 2)}"
            return result

        case nodes.AssignExpr(target=target, value=value):
            return (
                f"{prefix}Assign\n"
                f"{format_node(target, indent + 2)}\n"
                f"{format_node(value, indent + 2)}"
            )

        case nodes.IfStmt(
            condition=condition,
            then_expr=then_expr,
            else_expr=else_expr,
        ):
            result = (
                f"{prefix}If\n"
                f"{format_node(condition, indent + 2)}\n"
                f"{format_node(then_expr, indent + 2)}"
            )
            if else_expr is not None:
                result += f"\n{format_node(else_expr, indent + 2)}"
            return result

        case nodes.Block(statements=statements):
            result = f"{prefix}Block"
            for statement in statements:
                result += f"\n{format_node(statement, indent + 2)}"
            return result

        case _:
            return f"{prefix}Unknown Node ({type(node).__name__})"


def format_ast(functions: list[nodes.Function]) -> str:
    return "\n".join(format_node(function) for function in functions)