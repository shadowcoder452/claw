from __future__ import annotations
from abstract import *
from enum import Enum, auto
from error_types import SemanticError

class Symbol(Enum):
    Variable = auto()
    Function = auto()
    
class SymTableError(Enum):
    FuncRedeclared = auto()
    FuncRedeclaredAsVar = auto()

class SymTable:
    def __init__(self, parent: SymTable | None = None):
        self.symbols: dict[str, Symbol] = {}
        self.parent = parent
        
    def lookup(self, name: str) -> Symbol | None:
        if name in self.symbols:
            return self.symbols[name]

        if self.parent is not None:
            return self.parent.lookup(name)

        return None
    
    def assign(self, sym_type: Symbol, name: str) -> SymTableError | None:
        if sym_type == Symbol.Function and name in self.symbols:
            if self.symbols[name] == Symbol.Function:
                # will be put in analyzer raise SemanticError(f"Cannot redeclare function '{name}'")
                return SymTableError.FuncRedeclared
            elif self.symbols[name] == Symbol.Variable:
                # will be put in analyzer raise SemanticError(f"Cannot redeclare variable '{name}' as function")
                return SymTableError.FuncRedeclaredAsVar
        
        self.symbols[name] = sym_type
        return None
        

class SemanticAnalyzer:
    def __init__(self, ast: list[Function]):
        self.ast = ast
        
    def analyze(self): pass