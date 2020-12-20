import os
import sys
import traceback
from typing import List, Callable, Dict, Set, Any

from gui.common import singleton
from gui.message_handler import MessageHandler, MessageLevel


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
            MessageHandler().emit(f"unhandlable exception occurred, please check the traceback", MessageLevel.ERROR)
            for h in self.hooks:
                h(exec_type, exec_value, exec_trackback)
        return hook

    def add_hook(self, fn):
        self.hooks.append(fn)

    def enable(self):
        self.oldhook = sys.excepthook
        sys.excepthook = self.create_hook()

    def disable(self):
        sys.excepthook = self.oldhook