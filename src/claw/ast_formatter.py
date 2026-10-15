import abstract


def format_node(node, indent: int = 0) -> str:
    prefix = " " * indent

    match node:
        case abstract.Function(name=name, parameters=parameters, body=body):
            params = ", ".join(param.value for param in parameters)
            return (
                f"{prefix}Function {name}({params})\n"
                f"{format_node(body, indent + 2)}"
            )

        case abstract.ExprStmt(expr=expr):
            return format_node(expression, indent)

        case abstract.NumberExpr(value=value):
            return f"{prefix}Number: {value.value}"

        case abstract.IdentifierExpr(value=value):
            return f"{prefix}Identifier: {value.value}"

        case abstract.BinaryOp(left=left, op=op, right=right):
            return (
                f"{prefix}BinaryOp: {op.value}\n"
                f"{format_node(left, indent + 2)}\n"
                f"{format_node(right, indent + 2)}"
            )

        case abstract.CallExpr(callee=callee, arguments=arguments):
            result = f"{prefix}Call: {callee.value.value}"
            for argument in arguments:
                result += f"\n{format_node(argument, indent + 2)}"
            return result

        case abstract.AssignExpr(target=target, value=value):
            return (
                f"{prefix}Assign\n"
                f"{format_node(target, indent + 2)}\n"
                f"{format_node(value, indent + 2)}"
            )

        case abstract.IfStmt(
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

        case abstract.Block(statements=statements):
            result = f"{prefix}Block"
            for statement in statements:
                result += f"\n{format_node(statement, indent + 2)}"
            return result

        case _:
            raise TypeError(f"Unknown AST node: {type(node).__name__}")


def format_ast(functions: list[abstract.Function]) -> str:
    return "\n".join(format_node(function) for function in functions)