from dataclasses import dataclass
from pathlib import Path

from . import _sb3_obj as sb3
from . import _sb3_reporter as sb3_rp
from . import nodes
from .lexer import TokenType
from .type_aliases import Program

NULL_VALUE = "--CLAW-NULL-VALUE--\x00"


@dataclass
class CompiledExpr:
    prelude: list[sb3.Block]
    reporter: list


class CodeGenerator:
    def __init__(self, ast: Program) -> None:
        self.ast = ast
        self.project = sb3.Project(
            [sb3.Target(True, "Stage"), sb3.Target(False, "Cat")]
        )
        self.target = self.project.targets[1]
        self.stage = self.project.targets[0]
        self.target.costumes.append(
            sb3.Costume(
                "costume1",
                Path(__file__).parent / "placeholder_assets/cat.svg",
                0,
                0,
            )
        )
        self.stage.costumes.append(
            sb3.Costume(
                "backdrop1",
                Path(__file__).parent / "placeholder_assets/blank.svg",
                0,
                0,
            )
        )
        self._current_script: list[sb3.Block] = []
        self.variables: dict[str, sb3.Variable] = {}

    def _link_current_script(self, parent: sb3.Block) -> None:
        """Link collected command blocks under their script's hat block."""
        previous = parent

        for block in self._current_script:
            block.parent = previous
            previous.next = block
            self.target.blocks[block.id] = block
            previous = block

        self._current_script.clear()

    def _declare_var(self, name: str) -> None:
        variable = sb3.Variable(name, NULL_VALUE)
        self.target.variables[variable.id] = variable
        self.variables[variable.name] = variable
        
    def _compile_binary_op(self, node: nodes.BinaryOp, opcode: str, left_input: str, right_input: str) -> CompiledExpr:
        left = self.visit_expr(node.left)
        right = self.visit_expr(node.right)

        block = sb3.Block(
            opcode,
            inputs={
                left_input: left.reporter,
                right_input: right.reporter,
            },
        )
        self.target.blocks[block.id] = block

        # Connected reporter blocks need this operator as their parent.
        for operand in (left, right):
            if operand.reporter[0] == sb3_rp.INPUT_NO_SHADOW:
                child = self.target.blocks[operand.reporter[1]]
                child.parent = block

        return CompiledExpr(
            [*left.prelude, *right.prelude],
            [sb3_rp.INPUT_NO_SHADOW, block.id],
        )

    def generate(self) -> sb3.Project:
        self._temp_idx = 0
        for node in self.ast:
            self.visit(node)

        return self.project

    def generate_at(self, filename: str | Path) -> None:
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
        hat = sb3.Block("event_whenflagclicked", top_level=True)
        self.target.blocks[hat.id] = hat
        self.visit(node.body)
        self._link_current_script(hat)
        
    def visit_Identifier(self, node: nodes.Identifier) -> CompiledExpr: raise NotImplementedError()
        

    def visit_Assign(self, node: nodes.Assign) -> CompiledExpr:
        """Compile an assignment into a command prelude and variable reporter."""
        name = node.target.value.value
        value = self.visit_expr(node.value)
        var = self.variables[name]

        fields: dict[str, object] = {
            "VARIABLE": [var.name, var.id],
        }
        inputs: dict[str, object] = {
            "VALUE": value.reporter,
        }
        set_block = sb3.Block("data_setvariableto", inputs=inputs, fields=fields)

        # If the value is another reporter block, make this set block its parent.
        if value.reporter[0] == sb3_rp.INPUT_NO_SHADOW:
            child = self.target.blocks[value.reporter[1]]
            child.parent = set_block

        var_reporter = [
            sb3_rp.INPUT_SAME_BLOCK_SHADOW,
            [sb3_rp.VARIABLE, var.name, var.id],
        ]
        return CompiledExpr([*value.prelude, set_block], var_reporter)

    def visit_BinaryOp(self, node: nodes.BinaryOp) -> CompiledExpr:
        match node.op._type:
            case TokenType.Plus:
                return self._compile_binary_op(
                   node, "operator_add", "NUM1", "NUM2"
                )
                
            case TokenType.Minus:
                return self._compile_binary_op(
                    node, "operator_subtract", "NUM1", "NUM2"
                )
                
            case TokenType.Mul:
                return self._compile_binary_op(
                    node, "operator_multiply", "NUM1", "NUM2"
                )
                
            case TokenType.Div:
                return self._compile_binary_op(
                    node, "operator_divide", "NUM1", "NUM2"
                )

            case _:
                raise NotImplementedError(
                    f"unsupported binary operator: {node.op.value}"
                )

    def visit_Number(self, node: nodes.Number) -> CompiledExpr:
        reporter = [
            sb3_rp.INPUT_SAME_BLOCK_SHADOW,
            [sb3_rp.MATH_NUM_PRIMITIVE, node.value.value],
        ]
        return CompiledExpr([], reporter)