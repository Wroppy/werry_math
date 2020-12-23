import sys
from typing import Set

from gui.common import singleton
from gui.message_handler import MessageHandler, MessageLevel


@singleton
class PathHandler:
    external: Set[str]

    def __init__(self):
        self.external = set()

    def add_to_path(self, path: str):
        if path in sys.path:
            return
        self.external.add(path)
        sys.path.append(path)
        self.update_syspath()

    def insert_to_path(self, path: str, index: int = 0):
        self.external.add(path)
        sys.path.insert(index, path)
        self.update_syspath()

    def update_syspath(self):
        MessageHandler().emit(f"updated path: {sys.path}", MessageLevel.DEBUG)
        MessageHandler().emit(f"updated external: {self.external}", MessageLevel.DEBUG)
