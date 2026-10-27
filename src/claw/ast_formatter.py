from .nodes import Expression, Statement
from .type_aliases import Program
from .nodes import (
    Function,
    ExprStmt,
    Number,
    BinaryOp,
    Return,
    Identifier,
    Call,
    Assign,
    If,
    Block,
    VarDecl,
    WhenFlagClicked,
)


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

        case WhenFlagClicked(body=body):
            return (
                f"{prefix}WhenFlagClicked\n"
                f"{format_node(body, indent + 2)}"
            )

        case ExprStmt(expr=expr):
            return format_node(expr, indent)

        case Number(value=value):
            return f"{prefix}Number: {value.value}"

        case Identifier(value=value):
            return f"{prefix}Identifier: {value.value}"

        case BinaryOp(left=left, op=op, right=right):
            return (
                f"{prefix}BinaryOp: {op.value}\n"
                f"{format_node(left, indent + 2)}\n"
                f"{format_node(right, indent + 2)}"
            )

        case Call(callee=callee, arguments=arguments):
            result = f"{prefix}Call: {callee.value.value}"
            for argument in arguments:
                result += f"\n{format_node(argument, indent + 2)}"
            return result

        case Assign(target=target, value=value):
            return (
                f"{prefix}Assign\n"
                f"{format_node(target, indent + 2)}\n"
                f"{format_node(value, indent + 2)}"
            )

        case If(
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

        case VarDecl(name=name):
            return (
                f"VarDecl\n"
                f"{format_node(node.name, indent + 2)}"
            )

        case Return(expr=expr):
            if expr is None:
                return f"{prefix}Return"
            return (
                f"{prefix}Return\n"
                f"{format_node(expr, indent + 2)}"
            )

        case _:
            return f"{prefix}unknown node {type(node).__name__}"


def format_ast(functions: Program) -> str:
    return "\n".join(format_node(function) for function in functions)