from __future__ import annotations
import hashlib
import uuid
import json
import shutil
from pathlib import Path


class Costume:
    """Represents an image costume belonging to a Scratch target."""

    def __init__(
        self,
        name: str,
        *,
        source_path: str,
        rotation_center_x: float,
        rotation_center_y: float,
    ) -> None:
        self.name = name
        self.source_path = Path(source_path)
        self.rotation_center_x = rotation_center_x
        self.rotation_center_y = rotation_center_y
        
    @property
    def data_format(self) -> str:
        return self.source_path.suffix.lstrip(".").lower()
        
    @property
    def asset_id(self) -> str:
        return hashlib.md5(self.source_path.read_bytes()).hexdigest()
    
    @property
    def md5ext(self) -> str:
        return f"{self.asset_id}.{self.data_format}"

    def serialize(self) -> dict[str, object]:
        return {
            "name": self.name,
            "assetId": self.asset_id,
            "dataFormat": self.data_format,
            "rotationCenterX": self.rotation_center_x,
            "rotationCenterY": self.rotation_center_y,
            "bitmapResolution": 1,
            "md5ext": self.md5ext,
        }


class Sound:
    """Represents an audio asset belonging to a Scratch target."""

    def __init__(
        self,
        name: str,
        *,
        source_path: str,
        rate: int,
        sample_count: int,
    ) -> None:
        self.name = name
        self.source_path = Path(source_path)
        self.rate = rate
        self.sample_count = sample_count
        
    @property
    def data_format(self) -> str:
        return self.source_path.suffix.lstrip(".").lower()
        
    @property
    def asset_id(self) -> str:
        return hashlib.md5(self.source_path.read_bytes()).hexdigest()
    
    @property
    def md5ext(self) -> str:
        return f"{self.asset_id}.{self.data_format}"

    def serialize(self) -> dict[str, object]:
        return {
            "name": self.name,
            "assetId": self.asset_id,
            "dataFormat": self.data_format,
            "format": "",
            "rate": self.rate,
            "sampleCount": self.sample_count,
            "md5ext": self.md5ext,
        }
        
class Procedure:
    """Represents a custom Scratch procedure."""

    def __init__(
        self,
        name: str,
        *,
        arguments: list[str] | None = None,
        body: list[Block] | None = None,
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
            raise ValueError("defaults must have one value per argument")

        self.argument_ids = [uuid.uuid4().hex for _ in self.arguments]
        self.argument_reporters: list[Block] = []

    @property
    def proccode(self) -> str:
        return self.name + "".join(" %s" for _ in self.arguments)

    def mutation(self, *, prototype: bool = True) -> dict[str, object]:
        result: dict[str, object] = {
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
        definition = Block(
            opcode="procedures_definition",
            inputs={},
            top_level=True,
        )
        prototype = Block(
            opcode="procedures_prototype",
            inputs={},
            shadow=True,
            parent=definition,
            mutation=self.mutation(),
        )
        definition.inputs["custom_block"] = [1, prototype.id]

        self.argument_reporters = []
        for argument_id, argument_name in zip(self.argument_ids, self.arguments):
            reporter = Block(
                opcode="argument_reporter_string_number",
                fields={"VALUE": [argument_name, None]},
                shadow=True,
                parent=prototype,
            )
            prototype.inputs[argument_id] = [1, reporter.id]
            self.argument_reporters.append(reporter)

        return definition, prototype

class Block:
    """Represents a single block in a Scratch script."""

    def __init__(
        self,
        opcode: str,
        *,
        inputs: dict[str, object] | None = None,
        fields: dict[str, object] | None = None,
        mutation: dict[str, object] | None = None,
        shadow: bool = False,
        top_level: bool = False,
        next: Block | None = None,
        parent: Block | None = None,
        id: str | None = None,
    ) -> None:
        self.opcode = opcode
        self.inputs = {} if inputs is None else inputs
        self.fields = {} if fields is None else fields
        self.mutation = mutation
        self.shadow = shadow
        self.top_level = top_level
        self.next = next
        self.parent = parent
        self.id = uuid.uuid4().hex if id is None else id

    def serialize(self) -> dict[str, object]:
        result = {
            "opcode": self.opcode,
            "inputs": self.inputs,
            "fields": self.fields,
            "shadow": self.shadow,
            "topLevel": self.top_level,
            "next": self.next.id if self.next is not None else None,
            "parent": self.parent.id if self.parent is not None else None,
        }

        if self.top_level:
            result["x"] = 0
            result["y"] = 0
        
        if self.mutation is not None:
            result["mutation"] = self.mutation

        return result


class Variable:
    """Represents a Scratch variable."""

    def __init__(
        self,
        name: str,
        value: str | int | float | bool = 0,
        id: str | None = None,
    ) -> None:
        self.id = uuid.uuid4().hex if id is None else id
        self.name = name
        self.value = value

    def serialize(self) -> list[str | int | float | bool]:
        return [self.name, self.value]


class Target:
    """Represents a Scratch target, either the stage or a sprite."""

    def __init__(
        self,
        is_stage: bool,
        name: str,
        variables: list[Variable] | None = None,
        blocks: dict[str, Block] | None = None,
        costumes: list[Costume] | None = None,
        sounds: list[Sound] | None = None,
        *,
        current_costume: int = 0,
        volume: float = 100,
        visible: bool = True,
        x: float = 0,
        y: float = 0,
        size: float = 100,
        direction: float = 90,
    ) -> None:
        self.is_stage = is_stage
        self.name = name

        self.variables: dict[str, Variable] = {
            variable.id: variable
            for variable in (variables or [])
        }

        self.blocks = {} if blocks is None else blocks
        self.costumes = [] if costumes is None else costumes
        self.sounds = [] if sounds is None else sounds

        self.current_costume = current_costume
        self.volume = volume
        self.visible = visible
        self.x = x
        self.y = y
        self.size = size
        self.direction = direction

    def serialize(self) -> dict[str, object]:
        result = {
            "isStage": self.is_stage,
            "name": "Stage" if self.is_stage else self.name,
            "variables": {
                variable_id: variable.serialize()
                for variable_id, variable in self.variables.items()
            },
            "lists": {},
            "broadcasts": {},
            "blocks": {
                block_id: block.serialize()
                for block_id, block in self.blocks.items()
            },
            "comments": {},
            "costumes": [
                costume.serialize()
                for costume in self.costumes
            ],
            "sounds": [
                sound.serialize()
                for sound in self.sounds
            ],
            "currentCostume": self.current_costume,
            "volume": self.volume,
        }

        if self.is_stage:
            result.update({
                "tempo": 60,
                "videoTransparency": 50,
                "videoState": "on",
            })
        else:
            result.update({
                "visible": self.visible,
                "x": self.x,
                "y": self.y,
                "size": self.size,
                "direction": self.direction,
                "draggable": False,
                "rotationStyle": "all around",
                "layerOrder": 1,
            })

        return result


class Project:
    """Represents the entire project.json file."""

    def __init__(
        self,
        targets: list[Target] | None = None,
        *,
        extensions: list[str] | None = None,
        meta: dict[str, object] | None = None,
    ) -> None:
        self.targets = [] if targets is None else targets
        self.extensions = [] if extensions is None else extensions
        self.meta = {
            "semver": "3.0.0",
            "vm": "0.2.0",
            "agent": "Claw",
        } if meta is None else meta

    def serialize(self) -> dict[str, object]:
        return {
            "targets": [
                target.serialize()
                for target in self.targets
            ],
            "monitors": [],
            "extensions": self.extensions,
            "meta": self.meta,
        }

    def package(self, filename: str) -> None:
        """Package the project as a Scratch .sb3 file."""
        output_path = Path(f"{filename}.sb3")
        folder = Path(filename)

        folder.mkdir(parents=True, exist_ok=True)

        with open(folder / "project.json", "w", encoding="utf-8") as file:
            json.dump(
                self.serialize(),
                file,
                indent=4,
                ensure_ascii=False,
            )

        # Copy costume and sound assets.
        for target in self.targets:
            for asset in target.costumes + target.sounds:
                if not asset.source_path.exists():
                    raise FileNotFoundError(
                        f"Asset file not found: {asset.source_path}"
                    )

                shutil.copy2(
                    asset.source_path,
                    folder / asset.md5ext,
                )

        # Create the archive, then rename it to .sb3.
        archive = shutil.make_archive(
            filename,
            "zip",
            root_dir=folder,
        )

        Path(archive).replace(output_path)