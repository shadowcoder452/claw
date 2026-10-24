import json
import uuid
from ._sb3_obj import Block


class Procedure:
    """Represents a custom Scratch procedure."""

    def __init__(
        self,
        name: str,
        arguments: list[str] | None = None,
        body: list[Block] | None = None,
        *,
        defaults: list[str] | None = None,
        warp: bool = False,
    ) -> None:
        self.name = name
        self.arguments = [] if arguments is None else arguments
        self.body = [] if body is None else body
        self.defaults = (
            [""] * len(self.arguments)
            if defaults is None
            else defaults
        )
        self.warp = warp

        if len(self.defaults) != len(self.arguments):
            raise ValueError(
                "defaults must have one value per argument"
            )

        self.argument_ids = [
            uuid.uuid4().hex for _ in self.arguments
        ]

    @property
    def proccode(self) -> str:
        """Return the Scratch procedure signature."""
        return self.name + "".join(
            " %s" for _ in self.arguments
        )

    def mutation(self, *, prototype: bool = True) -> dict[str, object]:
        """Create Scratch procedure mutation metadata."""
        result = {
            "tagName": "mutation",
            "children": [],
            "proccode": self.proccode,
            "argumentids": json.dumps(self.argument_ids),
            "warp": json.dumps(self.warp),
        }

        if prototype:
            result["argumentnames"] = json.dumps(self.arguments)
            result["argumentdefaults"] = json.dumps(self.defaults)

        return result

    def build(self) -> tuple[Block, Block]:
        """Build and return the definition and prototype blocks."""
        definition = Block(
            opcode="procedures_definition",
            inputs={},
            top_level=True,
        )

        prototype = Block(
            opcode="procedures_prototype",
            inputs={
                argument_id: [
                    1,
                    Block(
                        opcode="argument_reporter_string_number",
                        fields={"VALUE": [argument_name, None]},
                        shadow=True,
                        parent=None,
                    ).id,
                ]
                for argument_id, argument_name
                in zip(self.argument_ids, self.arguments)
            },
            shadow=True,
            parent=definition,
            mutation=self.mutation(),
        )

        definition.inputs["custom_block"] = [1, prototype.id]

        return definition, prototype