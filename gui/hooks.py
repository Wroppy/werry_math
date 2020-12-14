import os
import sys
import traceback
from typing import List, Callable, Dict, Set, Any


# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
def singleton(cls_: Callable) -> type:
    """
    Implements a simple singleton decorator
    """

    class Singleton(cls_):  # type: ignore
        __instances: Dict[type, object] = {}
        __initialized: Set[type] = set()

        def __new__(cls, *args, **kwargs):
            if Singleton.__instances.get(cls) is None:
                Singleton.__instances[cls] = super().__new__(cls, *args, **kwargs)
            return Singleton.__instances[cls]

        def __init__(self, *args, **kwargs):
            if self.__class__ not in Singleton.__initialized:
                Singleton.__initialized.add(self.__class__)
                super().__init__(*args, **kwargs)

    return Singleton


@singleton
class ExceptionHooks:
    """
    Singleton to manage sys.excepthook
    """
    hooks: List[Callable]
    oldhook: Any
    ignore: str

    def __init__(self):
        self.hooks = []
        self.oldhook = sys.excepthook
        sys.excepthook = self.create_hook()

    def create_hook(self):
        def hook(exec_type, exec_value, exec_trackback):
            string = "".join(traceback.format_exception(exec_type, exec_value, exec_trackback))
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stderr__
            sys.stderr = sys.__stderr__
            print(string)
            for h in self.hooks:
                h(exec_type, exec_value, exec_trackback)

            os._exit(1)
        return hook

    def add_hook(self, fn):
        self.hooks.append(fn)

    def enable(self):
        self.oldhook = sys.excepthook
        sys.excepthook = self.create_hook()

    def disable(self):
        sys.excepthook = self.oldhook