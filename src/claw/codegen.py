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

    def _link_current_script(self, parent: sb3.Block | None = None) -> None:
        if not self._current_script:
            return
        
        if parent is None and len(self._current_script) == 1:
            block = self._current_script[0]
            self.target.blocks[block.id] = block
            return
        
        previous = parent if not parent is None else self._current_script[0]
        
        for block in self._current_script:
            block.parent = previous
            previous.next = block
            self.target.blocks[block.id] = block
            previous = block

        self._current_script = []

    def _declare_var(self, name: str) -> None:
        variable = sb3.Variable(name, NULL_VALUE)
        self.target.variables[variable.id] = variable
        self.variables[variable.name] = variable
        
    def _reporter_has_block_id(self, input_value: list):
        if isinstance(input_value[1], str) and input_value[1] in self.target.blocks:
            return True
        return False
        
    def _set_input_child_parent(self, input_value: list, parent: sb3.Block) -> None:
        if self._reporter_has_block_id(input_value):
            self.target.blocks[input_value[1]].parent = parent

    def _compile_substack(
        self,
        statement: nodes.Statement | None,
        parent: sb3.Block,
        input_name: str,
    ) -> None:
        """Compile a statement into a control block's substack input."""
        if statement is None:
            return

        outer_script = self._current_script
        self._current_script = []
        try:
            self.visit(statement)
            body_blocks = self._current_script
        finally:
            self._current_script = outer_script

        if not body_blocks:
            return

        reporter = [
            sb3_rp.INPUT_NO_SHADOW,
            body_blocks[0].id,
        ]
        parent.inputs[input_name] = reporter

        self._current_script = body_blocks
        try:
            self._link_current_script()
        finally:
            self._current_script = outer_script

        self._set_input_child_parent(reporter, parent)
        
    def _compile_binary_op(
        self,
        opcode: str,
        left_reporter: list,
        right_reporter: list,
        left_input: str,
        right_input: str
    ) -> list:

        bin_op = sb3.Block(
            opcode,
            inputs={
                left_input: left_reporter,
                right_input: right_reporter,
            },
        )
        self.target.blocks[bin_op.id] = bin_op
                
        self._set_input_child_parent(left_reporter, bin_op)
        self._set_input_child_parent(right_reporter, bin_op)

        return [sb3_rp.INPUT_NO_SHADOW, bin_op.id]
    
    def _compile_unary_op(
        self,
        opcode: str,
        reporter: list,
        _input: str
    ) -> list:

        un_op = sb3.Block(
            opcode,
            inputs={
                _input: reporter
            },
        )
        self.target.blocks[un_op.id] = un_op
                
        self._set_input_child_parent(reporter, un_op)

        return [sb3_rp.INPUT_NO_SHADOW, un_op.id]

    def generate(self) -> sb3.Project:
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
        
    def visit_If(self, node: nodes.If) -> None:
        condition = self.visit_expr(node.condition)
        self._current_script.extend(condition.prelude)

        is_boolean = (
            isinstance(node.condition, nodes.BinaryOp)
            and node.condition.op._type is TokenType.Equal
        )

        if not is_boolean:
            zero = [
                sb3_rp.INPUT_SAME_BLOCK_SHADOW,
                [sb3_rp.MATH_NUM_PRIMITIVE, 0],
            ]

            equals_zero = self._compile_binary_op(
                "operator_equals",
                condition.reporter,
                zero,
                "OPERAND1",
                "OPERAND2",
            )

            condition.reporter = self._compile_unary_op(
                "operator_not",
                equals_zero,
                "OPERAND",
            )

        has_else = node._else is not None
        opcode = "control_if_else" if has_else else "control_if"
        if_block = sb3.Block(
            opcode,
            inputs={"CONDITION": condition.reporter},
        )
        self._set_input_child_parent(condition.reporter, if_block)

        self._compile_substack(node.then, if_block, "SUBSTACK")
        self._compile_substack(node._else, if_block, "SUBSTACK2")

        self._current_script.append(if_block)
        
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
        
        self._set_input_child_parent(value.reporter, set_block)

        reporter = [
            sb3_rp.INPUT_DIFFERENT_BLOCK_SHADOW,
            [sb3_rp.VARIABLE, var.name, var.id],
            [sb3_rp.MATH_NUM_PRIMITIVE, 0],
        ]
        
        return CompiledExpr([*value.prelude, set_block], reporter)

    def visit_BinaryOp(self, node: nodes.BinaryOp) -> CompiledExpr:
        left = self.visit_expr(node.left)
        right = self.visit_expr(node.right)
        
        match node.op._type:
            case TokenType.Plus:
                return CompiledExpr(
                    [*left.prelude, *right.prelude],
                    self._compile_binary_op("operator_add", left.reporter, right.reporter, "NUM1", "NUM2")
                )
                
            case TokenType.Minus:
                return CompiledExpr(
                    [*left.prelude, *right.prelude],
                    self._compile_binary_op("operator_subtract", left.reporter, right.reporter, "NUM1", "NUM2")
                )
                
            case TokenType.Mul:
                return CompiledExpr(
                    [*left.prelude, *right.prelude],
                    self._compile_binary_op("operator_multiply", left.reporter, right.reporter, "NUM1", "NUM2")
                )
                
            case TokenType.Div:
                return CompiledExpr(
                    [*left.prelude, *right.prelude],
                    self._compile_binary_op("operator_divide", left.reporter, right.reporter, "NUM1", "NUM2")
                )
                
            case TokenType.Equal:
                return CompiledExpr(
                    [*left.prelude, *right.prelude],
                    self._compile_binary_op("operator_equals", left.reporter, right.reporter, "OPERAND1", "OPERAND2")
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
    
    def visit_Identifier(self, node: nodes.Identifier) -> CompiledExpr:
        var = self.variables[node.value.value]
        reporter = [
            sb3_rp.INPUT_DIFFERENT_BLOCK_SHADOW,
            [sb3_rp.VARIABLE, var.name, var.id],
            [sb3_rp.TEXT_PRIMITIVE, ""],
        ]
        return CompiledExpr([], reporter)
