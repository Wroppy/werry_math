from typing import Any, Callable, Dict, Set


# https://medium.com/@mgarod/dynamically-add-a-method-to-a-class-in-python-c49204b85bd6
def add_method_to(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
        return None

    return decorator


# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
def singleton(cls_: Callable) -> type:
    """
    Implements a simple singleton decorator
    """

    class Singleton(cls_):  # type: ignore
        __instance = None
        __initialized = False

        def __new__(cls, *args, **kwargs):
            if Singleton.__instance is None:
                Singleton.__instance = super().__new__(cls)
            return Singleton.__instance

        def __init__(self, *args, **kwargs):
            if Singleton.__initialized:
                return
            Singleton.__initialized = True
            super().__init__(*args, **kwargs)

    return Singleton


def type_to_str(obj: Any):
    """
    Return the custom string version of this type/variable
    :param obj:
    :return:
    """
    call = True
    try:
        obj = obj()
    except:
        call = False

    if call:
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
