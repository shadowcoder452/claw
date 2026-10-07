from __future__ import annotations
from abstract import *
from enum import Enum, auto
from error_types import SemanticError, SemanticWarning
from scratch_limits import *

class Symbol(Enum):
    Variable = auto()
    Function = auto()
    
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
    
    def assign(self, symbol_type: Symbol, name: str) -> SymbolTableError | None:
        if symbol_type == Symbol.Function and name in self.symbols:
            if self.symbols[name] == Symbol.Function:
                return SymbolTableError.FuncRedeclared
            elif self.symbols[name] == Symbol.Variable:
                return SymbolTableError.VarRedeclaredAsFunc
        
        self.symbols[name] = symbol_type
        return None
        

class SemanticAnalyzer:
    def __init__(self, ast: list[Function]):
        self.symbols = SymbolTable()
        self.ast = ast
        self.warnings: list[SemanticWarning] = []
        
    def analyze(self):
        for fn in self.ast:
            self.visit(fn)
            
    def visit(self, node):
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        
        if method == None:
            raise SemanticError(node.span, f"[Internal] Semantic Analyzer: No visitor for '{type(node).__name__}'")
        
        return method(node)
    
    def visit_Function(self, node: Function):
        fn = self.symbols.assign(Symbol.Function, node.name)

        if fn == SymbolTableError.FuncRedeclared:
            raise SemanticError(node.span, f"Cannot redeclare function '{node.name}'")
        elif fn == SymbolTableError.VarRedeclaredAsFunc:
            raise SemanticError(node.span, f"Cannot redeclare variable '{node.name}' as function")

        old_symbols = self.symbols
        self.symbols = SymbolTable(old_symbols)

        for param in node.parameters:
            self.symbols.assign(Symbol.Variable, param.value)
        
        self.visit(node.body)

        self.symbols = old_symbols
        
    def visit_NumberExpr(self, node: NumberExpr):
        value = int(node.value.value)

        if value > MAX_SAFE_INTEGER:
            self.warnings.append(SemanticWarning(
                node.span,
                f"Integer constant is too large and cannot be represented exactly"
            ))
            
    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)
        
    def visit_IdentifierExpr(self, node: IdentifierExpr):
        self.symbols.assign(Symbol.Variable, node.value.value)