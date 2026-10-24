from .nodes import (
    Function,
    ExprStmt,
    NumberExpr,
    BinaryOp,
    ReturnStmt,
    IdentifierExpr,
    CallExpr,
    AssignExpr,
    IfStmt,
    Block,
    VarDeclStmt,
)
from .nodes import Expression, Statement
from .types import Program


def format_node(node: Expression | Statement, indent: int = 0) -> str:
    prefix = " " * indent

    match node:
        case Function(name=name, parameters=parameters, body=body):
            parameters_list = []

            for param in parameters:
                parameters_list.append(format_node(param, indent + 2))

            if parameters_list:
                parameters_str = '\n'.join(parameters_list) + '\n'
            else:
                parameters_str = ""

            return (
                f"{prefix}Function\n"
                f"{format_node(name, indent + 2)}\n"
                f"{parameters_str}"
                f"{format_node(body, indent + 2)}"
            )

        case ExprStmt(expr=expr):
            return format_node(expr, indent)

        case NumberExpr(value=value):
            return f"{prefix}Number: {value.value}"

        case IdentifierExpr(value=value):
            return f"{prefix}Identifier: {value.value}"

        case BinaryOp(left=left, op=op, right=right):
            return (
                f"{prefix}BinaryOp: {op.value}\n"
                f"{format_node(left, indent + 2)}\n"
                f"{format_node(right, indent + 2)}"
            )

        case CallExpr(callee=callee, arguments=arguments):
            result = f"{prefix}Call: {callee.value.value}"
            for argument in arguments:
                result += f"\n{format_node(argument, indent + 2)}"
            return result

        case AssignExpr(target=target, value=value):
            return (
                f"{prefix}Assign\n"
                f"{format_node(target, indent + 2)}\n"
                f"{format_node(value, indent + 2)}"
            )

        case IfStmt(
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

        case Block(statements=statements):
            result = f"{prefix}Block"
            for statement in statements:
                result += f"\n{format_node(statement, indent + 2)}"
            return result

        case VarDeclStmt(name=name):
            return (
                f"VarDecl\n"
                f"{format_node(node.name, indent + 2)}"
            )

        case ReturnStmt(expr=expr):
            if expr is None:
                return f"{prefix}ReturnStmt"
            return (
                f"{prefix}ReturnStmt\n"
                f"{format_node(expr, indent + 2)}"
            )

        case _:
            return f"{prefix}unknown node {type(node).__name__}"


def format_ast(functions: Program) -> str:
    return "\n".join(format_node(function) for function in functions)