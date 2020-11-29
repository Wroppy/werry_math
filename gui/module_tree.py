import importlib
import inspect
import os
from abc import ABC, abstractmethod
from typing import *

from PyQt5.QtGui import QStandardItem, QStandardItemModel

from gui.common import type_to_str


class CustomStandardItem(QStandardItem):
    def __init__(self, node: 'TreeNode', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(False)
        self.node = node


class TreeNode(ABC):
    parent: 'TreeNode'
    name: str
    path: str

    def __str__(self):
        return os.path.join(str(self.parent), self.name)

    @abstractmethod
    def parse(self):
        pass

    @abstractmethod
    def to_model(self) -> CustomStandardItem:
        pass

    def to_display_str(self) -> str:
        return self.name

    def get_root(self) -> 'TreeNode':
        parent = self.parent
        while not isinstance(parent, ModuleTree):
            parent = parent.parent
        return parent


class Variable(TreeNode, ABC):
    doc: str

    def to_import_path(self) -> str:
        return ".".join(
            os.path.join(self.parent.path[:-len(ModuleTree.file_extension)], self.name)[
            len(self.get_root().path) + 1:].split(
                os.path.sep))

    def to_console_str(self) -> str:
        return self.name


class Function(Variable):
    def __init__(self, parent: TreeNode, name: str, fn: Any, method: bool = False):
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

    def parse(self):
        pass

    def to_model(self) -> CustomStandardItem:
        if len(self.ret) == 0:
            to_str = f"FN {self.name}({self.args})"
        else:
            to_str = f"FN {self.name}({self.args})->{self.ret}"
        item = CustomStandardItem(self, to_str)
        item.setToolTip(self.doc)
        return item

    def to_console_str(self) -> str:
        if not self.method:
            return super(Function, self).to_console_str()
        return f"{self.parent.to_console_str()}.{self.name}"

    @staticmethod
    def match(parent: 'Module', name: str, path: str) -> List['Function']:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        methods = list(filter(lambda m: not m[0].startswith("__"), inspect.getmembers(module, inspect.isfunction)))

        results = []
        for fn_name, fn_callable in methods:
            if fn_callable.__module__ not in parent.to_import_prefix_str():
                continue
            results.append(Function(parent, fn_name, fn_callable))
        return results


class Class(Variable):
    nodes: List[Function]
    parent: 'Module'

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
            if fn.__module__ not in self.parent.to_import_prefix_str():
                continue

            function = Function(self, fn_name, fn, method=True)
            if fn_name == "__init__":
                self.constructor = function
            self.nodes.append(function)

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, f"CLS {self.name}")
        item.setToolTip(self.doc)
        for node in self.nodes:
            item.appendRow(node.to_model())
        return item

    @staticmethod
    def match(parent: 'Module', name: str, path: str) -> List['Class']:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        classes = list(filter(lambda m: not m[0].startswith("__"), inspect.getmembers(module, inspect.isclass)))

        results = []
        for cls_nam, cls in classes:
            if cls.__module__ not in parent.to_import_prefix_str():
                continue
            cls = Class(parent, cls_nam, cls)
            cls.parse()
            results.append(cls)

        return results


class Module(TreeNode):
    nodes: List[TreeNode]

    def __init__(self, parent: TreeNode, name: str):
        self.nodes = []
        self.parent = parent
        self.name = name
        self.path = os.path.join(parent.path, name)

    def parse(self):
        name = self.name[:-len(ModuleTree.file_extension)]
        functions = Function.match(self, name, self.path)
        self.nodes.extend(functions)
        classes = Class.match(self, name, self.path)
        self.nodes.extend(classes)
        # with open(self.path, "r") as f:
        #     content = str(f.readlines())
        #     Function.match(content)
        # for line in f.readlines():
        #     if "def" in line and Function.match(line[:-2]):
        #         line = line[:-2]
        #         fn = Function(self, line)
        #         self.nodes.append(fn)
        # import importlib.util
        # name = self.name[:-len(ModuleTree.file_extension)]
        # spec = importlib.util.spec_from_file_location(name, self.path)
        # module = importlib.util.module_from_spec(spec)
        # spec.loader.exec_module(module)
        # methods = list(filter(lambda m: not m[0].startswith("__"), inspect.getmembers(module, inspect.isfunction)))
        # for fn_name, fn_callable in methods:
        #     fn = Function(self, fn_name, fn_callable)
        #     self.nodes.append(fn)

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, self.to_display_str())
        for node in self.nodes:
            item.appendRow(node.to_model())
        return item

    def to_import_prefix_str(self) -> str:
        return ".".join(
            os.path.join(self.path[:-len(ModuleTree.file_extension)])[len(self.get_root().path) + 1:].split(
                os.path.sep))


class Package(TreeNode):
    nodes: List[TreeNode]

    def __init__(self, parent: TreeNode, name: str):
        self.nodes = []
        self.parent = parent
        self.name = name
        self.path = os.path.join(parent.path, name)

    def parse(self):
        folders = list(filter(lambda f: f not in ModuleTree.ignored_folders, next(os.walk(self.path))[1]))
        if len(folders) == 0:
            for file in next(os.walk(self.path))[2]:
                if not file.endswith(ModuleTree.file_extension):
                    continue
                if file in ModuleTree.ignored_files:
                    continue
                module = Module(self, file)
                module.parse()
                self.nodes.append(module)
        else:
            for folder in folders:
                if folder in ModuleTree.ignored_folders:
                    continue
                package = Package(self, folder)
                package.parse()
                self.nodes.append(package)

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, self.to_display_str())
        for node in self.nodes:
            item.appendRow(node.to_model())
        return item


class ModuleTree(TreeNode):
    ignored_folders = ['.idea', 'venv', '.git', '__pycache__', 'all', 'webserver', 'gui']
    ignored_files = ['__init__.py']
    file_extension = '.py'

    packages: List[Package]

    def __init__(self, path: str):
        self.packages = []
        self.path = path

    def __str__(self):
        return self.path

    def parse(self):
        for folder in next(os.walk(self.path))[1]:
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