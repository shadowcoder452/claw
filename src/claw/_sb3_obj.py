import uuid


class Costume:
    """Represents an image costume belonging to a Scratch target.

    Stores the metadata needed to describe a costume in a Scratch project.
    The actual image data is stored separately in the .sb3 archive.

    Attributes:
        name: The costume's display name in Scratch.
        asset_id: The identifier used to reference the image asset.
        data_format: The image format, such as 'svg' or 'png'.
        rotation_center_x: The horizontal coordinate of the costume's
            rotation center.
        rotation_center_y: The vertical coordinate of the costume's
            rotation center.
    """

    def __init__(
        self,
        name: str,
        asset_id: str,
        data_format: str,
        rotation_center_x: float,
        rotation_center_y: float,
    ):
        self.name = name
        self.asset_id = asset_id
        self.data_format = data_format
        self.rotation_center_x = rotation_center_x
        self.rotation_center_y = rotation_center_y


class Sound:
    """Represents an audio asset belonging to a Scratch target.

    Stores sound metadata for serialization into a Scratch project.
    The actual audio data is stored separately in the .sb3 archive.

    Attributes:
        name: The sound's display name in Scratch.
        asset_id: The identifier used to reference the audio asset.
        data_format: The audio format, typically 'wav' or 'mp3'.
        rate: The audio sample rate, when applicable.
        sample_count: The number of audio samples represented by the
            sound metadata.
    """

    def __init__(
        self,
        name: str,
        asset_id: str,
        data_format: str,
        rate: int,
        sample_count: int,
    ):
        self.name = name
        self.asset_id = asset_id
        self.data_format = data_format
        self.rate = rate
        self.sample_count = sample_count


class Block:
    """Represents a single block in a Scratch script.

    A block is identified by an opcode and may contain inputs, fields,
    and connections to other blocks. These properties describe the
    block's structure in Claw's internal representation.

    Block references are retained internally for next and parent.
    The serializer should convert these references into block IDs
    when generating Scratch's project.json format.

    Attributes:
        id: A unique identifier for the block.
        opcode: The Scratch opcode identifying the block's operation.
        inputs: Mapping of input names to their serialized input data.
        fields: Mapping of field names to their serialized field data.
        shadow: Whether this block is a shadow block.
        top_level: Whether this block is a top-level block, rather
            than a block connected to another block.
        next: The next block in the script, if one exists.
        parent: The block to which this block is connected, if any.
    """

    def __init__(
        self,
        opcode: str,
        inputs: dict | None = None,
        fields: dict | None = None,
        *,
        shadow: bool = False,
        top_level: bool = False,
        next: Block | None = None,
        parent: Block | None = None,
        id: str | None = None,
    ):
        self.opcode = opcode
        self.inputs = {} if inputs is None else inputs
        self.fields = {} if fields is None else fields
        self.shadow = shadow
        self.top_level = top_level
        self.next = next
        self.parent = parent
        self.id = uuid.uuid4().hex if id is None else id


class Variable:
    """Represents a Scratch variable.

    A variable stores a name, a current value, and an identifier.
    The identifier distinguishes variables that may share the same
    name but belong to different scopes.

    Attributes:
        id: A unique identifier for the variable.
        name: The variable's display name in Scratch.
        value: The variable's current value.
    """

    def __init__(
        self,
        name: str,
        value: str | int | float | bool = 0,
        id: str | None = None,
    ):
        self.id = uuid.uuid4().hex if id is None else id
        self.name = name
        self.value = value


class Target:
    """Represents a Scratch target, either the stage or a sprite.

    A target groups together the blocks, variables, costumes, sounds,
    and initial visual properties associated with a stage or sprite.

    Variables are stored in a dictionary keyed by variable ID, while
    blocks are stored in a dictionary keyed by block ID. Costumes and
    sounds are kept in lists because their ordering can matter.

    Attributes:
        is_stage: Whether this target represents the stage.
        name: The target's name. The stage is serialized as 'Stage'.
        variables: Mapping of variable IDs to Variable objects.
        blocks: Mapping of block IDs to Block objects.
        costumes: Ordered list of Costume objects belonging to the target.
        sounds: List of Sound objects belonging to the target.
        current_costume: Index of the initially selected costume.
        volume: The target's initial volume.
        visible: Whether the sprite is initially visible.
        x: The sprite's initial horizontal position.
        y: The sprite's initial vertical position.
        size: The sprite's initial size percentage.
        direction: The sprite's initial direction in degrees.
    """

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
    ):
        self.is_stage = is_stage
        self.name = name
        self.variables = {
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

"""Represents the entire project.json file.

    The project groups the targets together. It also
    provides the list of extensions and metadata required
    for the project to run.
    
    Attributes:
        targets: Targets in the project.
        extensions: Extensions required for the project to run.
        meta: Project format and software creating the project.
"""
class Project:
    def __init__(
        self,
        targets: list[Target],
        *,
        extensions: list[str] | None = None,
        meta: dict | None = None,
    ):
        self.targets = targets
        self.monitors = [] if monitors is None else monitors
        self.extensions = [] if extensions is None else extensions
        self.meta = {} if meta is None else meta