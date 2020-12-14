from typing import Any, Callable


def type_to_str(obj: Any):
    callable = True
    try:
        obj = obj()
    except:
        callable = False

    if callable:
        if isinstance(obj, bool):
            return "bool"
        elif isinstance(obj, int):
            return "int"
        elif isinstance(obj, str):
            return "str"
        elif isinstance(obj, float):
            return "float"
        elif obj is None:
            return "none"
        elif isinstance(obj, list):
            return "list"
        elif isinstance(obj, tuple):
            return "tuple"
        elif isinstance(obj, dict):
            return "dict"
        elif isinstance(obj, set):
            return "set"
    if isinstance(obj, Callable):
        return "callable"
    return str(type(obj))
