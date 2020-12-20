import importlib
import inspect
from typing import List


class ImportException(Exception):
    pass


def get_classes_from_file(name: str, path: str) -> List[object]:
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        classes = list(filter(lambda m: not m[0].startswith("__"), inspect.getmembers(module, inspect.isclass)))
    except:
        raise ImportException
    return classes


def get_functions_from_file(name: str, path: str) -> List[object]:
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        methods = list(filter(lambda m: not m[0].startswith("__"), inspect.getmembers(module, inspect.isfunction)))
    except:
        raise ImportException
    return methods
