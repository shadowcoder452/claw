
from __future__ import annotations

from enum import Enum, auto

from .nodes import (
    AssignExpr,
    BinaryOp,
    Block,
    CallExpr,
    ExprStmt,
    IdentifierExpr,
    IfStmt,
    NumberExpr,
    VarDeclStmt,
)
from .errors import SemanticError


class Symbol:
    pass


class Variable(Symbol):
    pass


class Function(Symbol):
    def __init__(self, parameters: list[str]):
        self.parameters = parameters


class SymbolTableError(Enum):
    FuncRedeclared = auto()
    VarRedeclaredAsFunc = auto()


class SymbolTable:
    def __init__(self, parent: SymbolTable | None = None):
        self.symbols: dict[str, Symbol] = {}
        self.parent = parent

    def lookup(self, name: str) -> Symbol | None:
        if name in self.symbols:
            return self.symbols[name]

        if self.parent is not None:
            return self.parent.lookup(name)

        return None

    def assign(self, symbol: Symbol, name: str) -> SymbolTableError | None:
        if name in self.symbols:
            existing = self.symbols[name]

            if isinstance(symbol, Function):
                if isinstance(existing, Function):
                    return SymbolTableError.FuncRedeclared
                if isinstance(existing, Variable):
                    return SymbolTableError.VarRedeclaredAsFunc

        self.symbols[name] = symbol
        return None


class SemanticAnalyzer:
    def __init__(self, ast: list):
        self.symbols = SymbolTable()
        self.ast = ast
        self.errors: list[SemanticError] = []

    def analyze(self):
        for statement in self.ast:
            self.visit(statement)

        return self.errors

    def visit(self, node):
        try:
            self._visit(node)
        except SemanticError as err:
            self.errors.append(err)

    def _visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)

        if method is None:
            raise SemanticError(
                node.span,
                f"internal semantic analyzer "
                f"has no visitor for {type(node).__name__}",
            )

        return method(node)

    def visit_Function(self, node):
        parameters = [param.value for param in node.parameters]

        if len(parameters) != len(set(parameters)):
            self.errors.append(SemanticError(node.span, "duplicate parameter"))

        error = self.symbols.assign(
            Function(parameters),
            node.name,
        )
        
        if error is SymbolTableError.FuncRedeclared:
            raise SemanticError(
                node.span,
                f"cannot redeclare function {node.name}",
            )
        elif error is SymbolTableError.VarRedeclaredAsFunc:
            raise SemanticError(
                node.span,
                f"cannot redeclare variable {node.name} as function",
            )

        old_symbols = self.symbols
        self.symbols = SymbolTable(old_symbols)

        try:
            for param in parameters:
                self.symbols.assign(Variable(), param)

            self.visit(node.body)
        finally:
            self.symbols = old_symbols

    def visit_NumberExpr(self, node: NumberExpr):
        pass

    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_AssignExpr(self, node: AssignExpr):
        name = node.target.value.value
        symbol = self.symbols.lookup(name)

        if symbol is None:
            raise SemanticError(
                node.span,
                f"assigned to undefined object `{name}`",
            )

        if isinstance(symbol, Function):
            raise SemanticError(
                node.span,
                "variable required as target of assignment",
            )

        self.visit(node.value)

    def visit_IdentifierExpr(self, node: IdentifierExpr):
        name = node.value.value

        if self.symbols.lookup(name) is None:
            raise SemanticError(
                node.span,
                f"undefined object `{name}` referenced",
            )

    def visit_CallExpr(self, node: CallExpr):
        name = node.callee.value.value
        symbol = self.symbols.lookup(name)

        if symbol is None:
            raise SemanticError(
                node.span,
                f"undefined object `{name}` referenced",
            )

        if isinstance(symbol, Variable):
            raise SemanticError(
                node.span,
                f"called object `{name}` is not a function",
            )

        if len(node.arguments) != len(symbol.parameters):
            raise SemanticError(
                node.span,
                f"expected {len(symbol.parameters)} arguments "
                f"but got {len(node.arguments)}",
            )

        for argument in node.arguments:
            self.visit(argument)

    def visit_Block(self, node: Block):
        for statement in node.statements:
            self.visit(statement)

    def visit_IfStmt(self, node: IfStmt):
        self.visit(node.condition)
        self.visit(node.then_expr)

        if node.else_expr is not None:
            self.visit(node.else_expr)

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_VarDeclStmt(self, node: VarDeclStmt):
        name = node.name.value.value

        if name in self.symbols.symbols:
            raise SemanticError(
                node.span,
                f"object `{name}` redefined",
            )

        self.symbols.assign(Variable(), name)
