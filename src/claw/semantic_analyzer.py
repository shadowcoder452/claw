from __future__ import annotations
from enum import Enum, auto
from .errors import SemanticError, Error
from .type_aliases import Program
from .nodes import (
    Assign,
    BinaryOp,
    Block,
    Call,
    ExprStmt,
    Expression,
    Function as FunctionNode,
    Identifier,
    If,
    Number,
    VarDecl,
    Return,
    Statement,
    WhenFlagClicked,
)

class Symbol:
    pass


class Variable(Symbol):
    pass


class Function(Symbol):
    def __init__(self, parameters: list[str]) -> None:
        self.parameters = parameters


class SymbolTableError(Enum):
    FuncRedeclared = auto()
    VarRedeclaredAsFunc = auto()


class SymbolTable:
    def __init__(self, parent: SymbolTable | None = None) -> None:
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
    def __init__(self, ast: Program) -> None:
        self.symbols = SymbolTable()
        self.symbols.assign(Function(["message"]), "say")
        self.symbols.assign(Function(["duration"]), "wait")
        self.ast = ast
        self.errors: list[SemanticError] = []

    def analyze(self) -> list[SemanticError]:
        for statement in self.ast:
            self.visit(statement)

        return self.errors

    def visit(self, node: Statement | Expression) -> None:
        try:
            self._visit(node)
        except SemanticError as err:
            self.errors.append(err)

    def _visit(self, node: Statement | Expression) -> None:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)

        if method is None:
            raise NotImplementedError(
                f"semantic analyzer has no visitor for `{type(node).__name__}`"
            )

        return method(node)

    def visit_WhenFlagClicked(self, node: WhenFlagClicked) -> None:
        self.visit(node.body)

    def visit_Function(self, node: FunctionNode) -> None:
        parameters = [param.value.value for param in node.parameters]
        name = node.name.value.value

        if len(parameters) != len(set(parameters)):
            self.errors.append(SemanticError(node.span, "duplicate parameter"))

        error = self.symbols.assign(
            Function(parameters),
            name,
        )
        
        if error is SymbolTableError.FuncRedeclared:
            raise SemanticError(
                node.span,
                f"cannot redeclare function `{name}`",
            )
        elif error is SymbolTableError.VarRedeclaredAsFunc:
            raise SemanticError(
                node.span,
                f"cannot redeclare variable `{name}` as function",
            )

        old_symbols = self.symbols
        self.symbols = SymbolTable(old_symbols)

        try:
            for param in parameters:
                self.symbols.assign(Variable(), param)

            self.visit(node.body)
        finally:
            self.symbols = old_symbols

    def visit_Number(self, node: Number) -> None:
        pass

    def visit_BinaryOp(self, node: BinaryOp) -> None:
        self.visit(node.left)
        self.visit(node.right)

    def visit_Assign(self, node: Assign) -> None:
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

    def visit_Identifier(self, node: Identifier) -> None:
        name = node.value.value

        if self.symbols.lookup(name) is None:
            raise SemanticError(
                node.span,
                f"undefined object `{name}` referenced",
            )

    def visit_Call(self, node: Call) -> None:
        name = node.callee.value.value
        symbol = self.symbols.lookup(name)

        if symbol is None:
            raise SemanticError(
                node.span,
                f"undefined object `{name}` referenced",
            )

        if not isinstance(symbol, Function):
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

    def visit_Block(self, node: Block) -> None:
        for statement in node.statements:
            self.visit(statement)

    def visit_If(self, node: If) -> None:
        self.visit(node.condition)
        self.visit(node.then)

        if node._else is not None:
            self.visit(node._else)

    def visit_ExprStmt(self, node: ExprStmt) -> None:
        self.visit(node.expr)

    def visit_VarDecl(self, node: VarDecl) -> None:
        name = node.name.value.value

        if name in self.symbols.symbols:
            raise SemanticError(
                node.span,
                f"object `{name}` redefined",
            )

        self.symbols.assign(Variable(), name)

    def visit_Return(self, node: Return) -> None:
        if node.expr is not None:
            self.visit(node.expr)