# Input structure codes
INPUT_SAME_BLOCK_SHADOW = 1
INPUT_NO_SHADOW = 2
INPUT_DIFFERENT_BLOCK_SHADOW = 3

# Primitive value codes
MATH_NUM_PRIMITIVE = 4
MATH_POSITIVE_NUM_PRIMITIVE = 5
MATH_WHOLE_NUM_PRIMITIVE = 6
MATH_INTEGER_PRIMITIVE = 7
MATH_ANGLE_PRIMITIVE = 8
COLOUR_PICKER = 9
TEXT_PRIMITIVE = 10
BROADCAST_OPTION = 11
VARIABLE = 12
LIST = 13


# Primitive constructors

def number(value: int | float) -> list[int | str]:
    return [MATH_NUM_PRIMITIVE, str(value)]


def positive_number(value: int | float) -> list[int | str]:
    return [MATH_POSITIVE_NUM_PRIMITIVE, str(value)]


def whole_number(value: int | float) -> list[int | str]:
    return [MATH_WHOLE_NUM_PRIMITIVE, str(value)]


def integer(value: int | float) -> list[int | str]:
    return [MATH_INTEGER_PRIMITIVE, str(value)]


def angle(value: int | float) -> list[int | str]:
    return [MATH_ANGLE_PRIMITIVE, str(value)]


def color(value: str) -> list[int | str]:
    return [COLOUR_PICKER, value]


def text(value: object) -> list[int | str]:
    return [TEXT_PRIMITIVE, str(value)]


def broadcast(name: str, broadcast_id: str) -> list[int | str]:
    return [BROADCAST_OPTION, name, broadcast_id]


def variable(name: str, variable_id: str) -> list[int | str]:
    return [VARIABLE, name, variable_id]


def list_primitive(name: str, list_id: str) -> list[int | str]:
    return [LIST, name, list_id]


# Input constructors

def input_shadow(value: object) -> list[object]:
    return [INPUT_SAME_BLOCK_SHADOW, value]


def input_no_shadow(value: object) -> list[object]:
    return [INPUT_NO_SHADOW, value]


def input_with_shadow(block_id: object, shadow_id: object) -> list[object]:
    return [INPUT_DIFFERENT_BLOCK_SHADOW, block_id, shadow_id]


# Common combined constructors

def input_number(value: int | float) -> list[object]:
    return input_shadow(number(value))


def input_text(value: object) -> list[object]:
    return input_shadow(text(value))


def input_color(value: str) -> list[object]:
    return input_shadow(color(value))


def input_broadcast(name: str, broadcast_id: str) -> list[object]:
    return input_shadow(broadcast(name, broadcast_id))


def input_variable(name: str, variable_id: str) -> list[object]:
    return input_shadow(variable(name, variable_id))


def input_list(name: str, list_id: str) -> list[object]:
    return input_shadow(list_primitive(name, list_id))
