UNDETERMINED = 0
LEFT_SIDE = -1
RIGHT_SIDE = 1


def add_paren(value: str) -> str:
    return f"({value})"


def add_brackets(value: str) -> str:
    return "{" + value + "}"

def add_square(value: str) -> str:
    return f"[{value}]"