from . import _sb3_obj as sb3
from . import _sb3_reporter as sb3_rp
from . import nodes
from .types import Program
from dataclasses import dataclass

CLAW_NULL = "__CLAW_NULL__\x00"

@dataclass
class CompiledExpr:
    prelude: list[sb3.Block]
    reporter: list

class CodeGenerator:
    def __init__(self, ast: Program) -> None:
        self.ast = ast
        self.project = sb3.Project([sb3.Target(True, "Stage"), sb3.Target(False, "Cat")])
        self.target = self.project.targets[1]
        self._current_script: list[sb3.Block] = []
        self.variables: dict[str, sb3.Variable] = {}
        
    def _link_current_script(self) -> sb3.Block:
        for i in range(len(self._current_script)):
            block = self._current_script[i]
            if i - 1 <= 0:
                block.parent = self._current_script[i - 1]
            if i + 1 < len(self._current_script):
                block.next = self._current_script[i + 1]
            self.target.blocks[block.id] = block
        
        block = self._current_script[0]
        self._current_script.clear()
        return block
        
    def _declare_var(self, name: str) -> None:
        variable = sb3.Variable(name, CLAW_NULL)
        self.target.variables[variable.id] = variable
        self.variables[variable.name] = variable
        

    def generate(self) -> sb3.Project:
        self._temp_idx = 0
        for node in self.ast:
            self.visit(node)

        return self.project

    def generate_at(self, filename: str) -> None:
        self.generate().package(filename)

    def visit(self, node: nodes.Statement | nodes.Expression) -> None:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)

        if method is None:
            raise NotImplementedError(
                f"code generator has no visitor for `{type(node).__name__}`"
            )

        method(node)
        
    def visit_expr(self, node: nodes.Expression) -> CompiledExpr:
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)

        if method is None:
            raise NotImplementedError(
                f"code generator has no visitor for `{type(node).__name__}`"
            )

        return method(node)

    def visit_VarDecl(self, node: nodes.VarDecl) -> None:
        self._declare_var(node.name.value.value)

    def visit_Block(self, node: nodes.Block) -> None:
        for statement in node.statements:
            self.visit(statement)
            
    def visit_ExprStmt(self, node: nodes.ExprStmt) -> None:
        self._current_script.extend(self.visit_expr(node.expr).prelude)
        
    def visit_WhenFlagClicked(self, node: nodes.WhenFlagClicked) -> None:
        block = sb3.Block("event_whenflagclicked", top_level=True)
        self.visit(node.body)
        block.next = self._link_current_script()
        self.target.blocks[block.id] = block
        
    def visit_Assign(self, node: nodes.Assign) -> CompiledExpr:
        """
        We need this since Scratch doesn't have an assignment reporter
        Example:
            3 + x = y = 2
        Prelude:
            y = 2
            x = y
        Produced Reporter:
            3 + x
        """
        name = node.target.value.value
        value = self.visit_expr(node.value)
        var = self.variables[name]
        
        fields: dict[str, object] = {
            "VARIABLE": [var.name, var.id]
        }
        
        inputs: dict[str, object] = {
            "VALUE": [1, value.reporter]
        }
        
        set_block = sb3.Block("data_setvariableto", inputs=inputs, fields=fields)
        var_reporter = [sb3_rp.VARIABLE, var.name, var.id]
        
        return CompiledExpr(
            [*value.prelude, set_block],
            var_reporter
        )
        
    def visit_BinaryOp(self, node: nodes.BinaryOp) -> CompiledExpr:
        
        
    def visit_Number(self, node: nodes.Number) -> CompiledExpr:
        return CompiledExpr(
            [], [sb3_rp.MATH_NUM_PRIMITIVE, node.value.value]
        )