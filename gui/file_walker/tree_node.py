import os
from abc import ABC, abstractmethod
from typing import Any

from PyQt5.QtGui import QStandardItem


# Custom standard item that contains the original node
class CustomStandardItem(QStandardItem):
    def __init__(self, node: 'TreeNode', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(False)
        self.node = node


class TreeNode(ABC):
    # parent node
    parent: 'TreeNode'
    # current node name
    name: str
    # current node file path
    path: str

    @abstractmethod
    def parse(self):
        """
        parse: method that sets up this node and its children
        """
        pass

    @abstractmethod
    def to_model(self) -> CustomStandardItem:
        """
        to_model: returns the qt model for this node
        :return:
        """
        pass

    def to_display_str(self) -> str:
        """
        to_display_str: returns the value displayed in the qtreeview
        """
        return self.name

    @staticmethod
    def is_ignored(obj: Any) -> bool:
        return hasattr(obj, "_ignored") and obj._ignored

    def get_root(self) -> 'TreeNode':
        """
        get_root: returns the root node of the tree
        """
        pass
