from ._sb3_obj import (
    Target,
    Block,
    Costume,
    Sound,
    Variable,
    Project,
)
from ._sb3_block_abstractions import Procedure
from .nodes import Statement
from .types import Program
import json
import shutil
from pathlib import Path

class CodeGenerator:
    def __init__(self, ast: Program) -> None:
        self.ast = ast
        self.project = Project([])

    def generate(self) -> Project:
        for node in self.ast:
            self.visit(node)

        return self.project
    
    def generate_at(self, filename: str) -> None:
        self.generate().package(filename)

    def visit(self, node: Statement) -> None:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)

        if method is None:
            raise NotImplementedError(
                f"code generator has no visitor for `{type(node).__name__}`"
            )

        return method(node)