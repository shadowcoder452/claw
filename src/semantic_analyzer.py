from __future__ import annotations
from abstract import *
from error_types import SemanticError, SemanticWarning
from scratch_limits import *


class Symbol:
    pass


class Variable(Symbol):
    pass


class FunctionStmt(Symbol):
    def __init__(self, parameters: list[str]):
        self.parameters = parameters


class SymbolTableError:
    FuncRedeclared = 0
    VarRedeclaredAsFunc = 1


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

            if isinstance(symbol, FunctionStmt):
                if isinstance(existing, FunctionStmt):
                    return SymbolTableError.FuncRedeclared
                elif isinstance(existing, Variable):
                    return SymbolTableError.VarRedeclaredAsFunc

        self.symbols[name] = symbol
        return None


class SemanticAnalyzer:
    def __init__(self, ast: list[FunctionStmt]):
        self.symbols = SymbolTable()
        self.ast = ast
        self.warnings: list[SemanticWarning] = []

    def analyze(self):
        for fn in self.ast:
            self.visit(fn)

    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)

        if method is None:
            raise SemanticError(
                node.span,
                f"[Internal] Semantic Analyzer: No visitor for '{type(node).__name__}'"
            )

        return method(node)

    def visit_Function(self, node: FunctionStmt):
        parameters = [param.value for param in node.parameters]

        fn = self.symbols.assign(
            FunctionStmt(parameters),
            node.name
        )

        if fn == SymbolTableError.FuncRedeclared:
            raise SemanticError(node.span, f"cannot redeclare function '{node.name}'")
        elif fn == SymbolTableError.VarRedeclaredAsFunc:
            raise SemanticError(node.span, f"cannot redeclare variable '{node.name}' as function")

        old_symbols = self.symbols
        self.symbols = SymbolTable(old_symbols)

        for param in parameters:
            self.symbols.assign(Variable(), param)

        self.visit(node.body)

        self.symbols = old_symbols

    def visit_NumberExpr(self, node: NumberExpr):
        value = int(node.value.value)

        if value > MAX_SAFE_INTEGER:
            self.warnings.append(SemanticWarning(
                node.span,
                "Integer constant is too large and cannot be represented exactly"
            ))

    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_AssignExpr(self, node: AssignExpr):
        name = node.target.value.value
        symbol = self.symbols.lookup(name)

        if isinstance(symbol, FunctionStmt):
            raise SemanticError(node.span, "variable required as target of assignment")

        self.symbols.assign(Variable(), name)

        self.visit(node.value)

    def visit_IdentifierExpr(self, node: IdentifierExpr):
        if self.symbols.lookup(node.value.value) is None:
            raise SemanticError(node.span, f"undefined object '{node.value.value}' referenced")

    def visit_CallExpr(self, node: CallExpr):
        symbol = self.symbols.lookup(node.callee.value.value)

        if symbol is None:
            raise SemanticError(node.span, f"undefined object '{node.callee.value.value}' referenced")

        if isinstance(symbol, Variable):
            raise SemanticError(
                node.span,
                f"called object '{node.callee.value.value}' is not a function"
            )

        if len(node.arguments) != len(symbol.parameters):
            raise SemanticError(
                node.span,
                f"expected {len(symbol.parameters)} arguments, "
                f"got {len(node.arguments)}"
            )

        for argument in node.arguments:
            self.visit(argument)
            
    def visit_Block(self, node: Block):
        for statement in node.statements:
            self.visit(statement)