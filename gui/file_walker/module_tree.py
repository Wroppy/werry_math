"""
This file handles the module tree discovery logic
I have yet to comment it but all it does is to create a QTreeView by scanning modules
"""
import importlib
import inspect
import os
from abc import ABC, abstractmethod
from typing import *

from PyQt5.QtGui import QStandardItemModel

from gui.common import type_to_str, add_method_to
from gui.file_walker.file_handle import get_classes_from_file, ImportException, get_functions_from_file
from gui.file_walker.tree_node import TreeNode, CustomStandardItem
from gui.message_handler import MessageHandler, MessageLevel
from gui.splash_screen import SplashScreen


class ModuleTree(TreeNode):
    """
    ModuleTree: is the root of the TreeNode hierarchy
    """
    # folder to ignore
    ignored_folders = ['.idea', 'venv', '.git', '__pycache__', 'release']
    # files to ignore
    ignored_files = ['__init__.py']
    # only files with this extension will be searched
    file_extension = '.py'

    # first layer packages
    packages: List[TreeNode]

    def __init__(self, path: str):
        self.packages = []
        self.path = path

    def parse(self):
        folders = next(os.walk(self.path))[1]
        folders_len = len(folders)
        i = 0
        for folder in folders:
            i += 1
            SplashScreen().displayMessage(f"parsing module {i}/{folders_len}")
            if folder in ModuleTree.ignored_folders:
                continue
            package = Package(self, folder)
            package.parse()
            self.packages.append(package)

    def to_model(self) -> QStandardItemModel:
        root = QStandardItemModel()
        root.invisibleRootItem()
        for package in self.packages:
            item = package.to_model()
            root.appendRow(item)
        return root


@add_method_to(TreeNode)
def get_root(self) -> TreeNode:
    parent = self.parent
    while True:
        try:
            parent = parent.parent
        except:
            break
    return parent


class Variable(TreeNode, ABC):
    # documentation
    doc: str
    parent: 'Module'

    def to_import_path(self) -> str:
        """
        to_import_path: returns the python import path of this variable
        :return:
        """
        path = ".".join(os.path.join(self.parent.path, self.name)[len(self.get_root().path) + 1:].split(os.path.sep))
        path = path.replace(ModuleTree.file_extension, '')
        return path

    def to_import_str(self) -> str:
        """
        to_import_str: returns the import statement using to_import_path
        :return:
        """
        path = self.to_import_path()
        module = '.'.join(path.split('.')[:-1])
        return f"from {module} import {self.name}"

    def parse(self):
        pass

    @staticmethod
    @abstractmethod
    def match(parent: 'Module', name: str) -> List[TreeNode]:
        """
        match: returns a list of nodes give a python module
        :param name: The python module name
        :param parent: The python module node
        """
        pass

    @abstractmethod
    def handleClicked(self, env: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """
        handleClicked: callback ran when the treenode is clicked
        :param env: interpreter environment
        :return: String to import, Text to render
        """
        pass

    def is_selectable(self) -> bool:
        return True


class Function(Variable):
    def __init__(self, parent: TreeNode, name: str, fn: Any, method: bool = False, inherited: str = None):
        self.parent = parent
        self.path = os.path.join(parent.path, name)
        self.name = name

        args = []
        ret = ""
        for anno in fn.__annotations__:
            value = fn.__annotations__[anno]
            if anno == 'return':
                ret = type_to_str(value)
            else:
                args.append(f"{anno}: {type_to_str(value)}")
        args = " ".join(args)
        doc = fn.__doc__

        self.args = args
        self.ret = ret
        if doc is None:
            self.doc = "No Doc Available"
        else:
            self.doc = '\n'.join(filter(lambda x: len(x) != 0, [line.strip() for line in doc.split('\n')]))
        self.method = method
        self.inherited = inherited

    def to_model(self) -> CustomStandardItem:
        to_str = f"{self.name}({self.args})"
        if self.method:
            to_str = f"MTD {to_str}"
        else:
            to_str = f"FN {to_str}"

        if self.inherited is not None:
            to_str = f"({self.inherited}) {to_str}"
        if len(self.ret) != 0:
            to_str += f"->{self.ret}"

        item = CustomStandardItem(self, to_str)
        item.setToolTip(self.doc)
        return item

    def handleClicked(self, env: Dict[str, Any]) -> Tuple[Optional[str], str]:
        import_str = None
        after = self.name
        if self.method:
            if self.parent.name not in env:
                import_str = self.parent.to_import_str()
                after = f"{self.parent.name}().{after}"
            else:
                after = '.' + after
        else:
            if self.name not in env:
                import_str = self.to_import_str()

        return import_str, after

    @staticmethod
    def match(parent: 'Module', name: str) -> List['Function']:
        methods = get_functions_from_file(name, parent.path)
        results = []
        for fn_name, fn_callable in methods:
            if fn_callable.__module__ not in parent.to_import_prefix_str():
                continue

            if TreeNode.is_ignored(fn_callable):
                continue

            results.append(Function(parent, fn_name, fn_callable))
        return results


class Class(Variable):
    nodes: List[Function]

    def __init__(self, parent: 'Module', name: str, cls: Any):
        self.path = os.path.join(parent.path, name)
        self.parent = parent
        self.name = name

        self.cls = cls

        doc = cls.__doc__
        if doc is None:
            self.doc = "No Doc Available"
        else:
            self.doc = '\n'.join(filter(lambda x: len(x) != 0, [line.strip() for line in doc.split('\n')]))

        self.constructor = None
        self.nodes = []

    def parse(self):
        result = inspect.getmembers(self.cls, predicate=inspect.isfunction)

        for fn_name, fn in result:
            if TreeNode.is_ignored(fn):
                continue

            function = Function(self, fn_name, fn, method=True)
            if fn_name == "__init__":
                self.constructor = function
            if fn.__module__ not in self.parent.to_import_prefix_str():
                function.inherited = fn.__module__
            self.nodes.append(function)

        self.nodes.sort(key=lambda n: str(n.inherited))
        self.nodes.sort(key=lambda n: n.inherited is not None)

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, f"CLS {self.name}")
        item.setToolTip(self.doc)
        for node in self.nodes:
            item.appendRow(node.to_model())
        return item

    def handleClicked(self, env: Dict[str, Any]) -> Tuple[Optional[str], str]:
        import_str = None
        after = self.name
        if self.name not in env:
            import_str = self.to_import_str()
        return import_str, after

    @staticmethod
    def match(parent: 'Module', name: str) -> List['Class']:
        classes = get_classes_from_file(name, parent.path)

        results = []
        for cls_nam, cls in classes:
            if cls.__module__ not in parent.to_import_prefix_str():
                continue
            if TreeNode.is_ignored(cls):
                continue

            cls = Class(parent, cls_nam, cls)
            cls.parse()
            results.append(cls)
        return results


class Module(TreeNode):
    nodes: List[TreeNode]
    has_error: bool

    def __init__(self, parent: TreeNode, name: str):
        self.nodes = []
        self.parent = parent
        self.name = name
        self.path = os.path.join(parent.path, name)
        self.has_error = False

    def parse(self):
        name = self.name[:-len(ModuleTree.file_extension)]
        try:
            functions = Function.match(self, name)
            self.nodes.extend(functions)
            classes = Class.match(self, name)
            self.nodes.extend(classes)
        except ImportException as e:
            MessageHandler().emit(f"unable to import python module: {self.name} {repr(e)}", MessageLevel.WARNING)
            self.has_error = True

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, self.to_display_str())
        for node in self.nodes:
            item.appendRow(node.to_model())
        return item

    def to_import_prefix_str(self) -> str:
        return ".".join(
            os.path.join(self.path[:-len(ModuleTree.file_extension)])[len(self.get_root().path) + 1:].split(
                os.path.sep))

    def to_display_str(self) -> str:
        string = super(Module, self).to_display_str()
        if self.has_error:
            string = "ERR " + string
        return string


class Package(TreeNode):
    nodes: List[TreeNode]

    def __init__(self, parent: TreeNode, name: str):
        self.nodes = []
        self.parent = parent
        self.name = name
        self.path = os.path.join(parent.path, name)

    def parse(self):
        result = next(os.walk(self.path))
        for folder in result[1]:
            if folder in ModuleTree.ignored_folders:
                continue
            package = Package(self, folder)
            package.parse()
            self.nodes.append(package)

        for file in result[2]:
            if not file.endswith(ModuleTree.file_extension):
                continue
            if file in ModuleTree.ignored_files:
                continue
            module = Module(self, file)
            module.parse()
            self.nodes.append(module)

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, self.to_display_str())
        for node in self.nodes:
            item.appendRow(node.to_model())
        return item
