import code
import inspect
import os
from abc import ABC, abstractmethod
from types import ModuleType
from typing import List, Union, Any, Callable, Dict, Optional

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import importlib.util

cdir = os.path.dirname(os.path.realpath(__file__))


def type_to_str(obj: Any):
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
    elif isinstance(obj, Callable):
        return "fn"
    return str(type(obj))


class CustomStandardItem(QStandardItem):
    def __init__(self, node: 'TreeNode', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setEditable(False)
        self.node = node


class CustomFilterModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)


class CustomTableModel(QAbstractTableModel):
    def __init__(self, header: List[Any], data: List[List[Any]]):
        super(CustomTableModel, self).__init__()
        self.data = data
        self.header = header

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.header[section])
            else:
                return super(CustomTableModel, self).headerData(section, orientation, role)


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


class Variable(TreeNode, ABC):
    doc: str

    def to_import_path(self) -> str:
        return ".".join(
            os.path.join(self.parent.path[:-len(ModuleTree.file_extension)], self.name)[len(cdir) + 1:].split(
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
            os.path.join(self.path[:-len(ModuleTree.file_extension)])[len(cdir) + 1:].split(
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
    ignored_folders = ['.idea', 'venv', '.git', '__pycache__', 'resources', 'all', 'webservers']
    ignored_files = ['__init__.py']
    file_extension = '.py'

    packages: List[Package]

    def __init__(self, path: str = str(cdir)):
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


# QTextEdit but better
class TerminalEmulator(QTextEdit):
    prompt: str = ">> "
    clearCommand: str = "clear"
    selectionWhiteListKeys: List[Qt.Key] = [Qt.Key_Left, Qt.Key_Right]

    history: List[str]
    currentIndex: int

    interpreter: code.InteractiveInterpreter

    localsUpdated: pyqtSignal = pyqtSignal(object)

    def __init__(self, *args, **kwargs):
        super(QTextEdit, self).__init__(*args, **kwargs)

        self.history = []
        self.currentIndex = 0

        self.interpreter = code.InteractiveInterpreter()

        # set font
        id = QFontDatabase.addApplicationFont("resources/consolas.ttf")
        fontstr = QFontDatabase.applicationFontFamilies(id)[0]
        font = QFont(fontstr, 0)
        self.setFont(font)

        self.setCurrentLine("")
        self.setStyleSheet("""
            QTextEdit {
                background: #2e2e2e;
                color: #ddd;
                font-size: 16px;
            }
        """)

    def write(self, message: str):
        self.appendLines(message.split('\n'))

    def clear(self):
        self.setText("")

    def importModule(self, module: str):
        self.executeCommand(f"from {module} import *")

    def writeFunction(self, var: Variable):
        import_path = var.to_import_path()
        root = import_path.split('.')[0]
        if isinstance(var, Class) or (isinstance(var, Function) and not var.method):
            if var.name not in self.interpreter.locals:
                if root not in self.interpreter.locals:
                    self.importModule(root)
                else:
                    self.appendCurrentLine(f"{import_path}")
                    self.setFocus()
                    return

        self.appendCurrentLine(var.to_console_str())
        self.setFocus()

    def executeCommand(self, command: str):
        current_line = self.currentLine()
        self.setCurrentLine(command)
        self.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifiers()))
        self.setCurrentLine(current_line)

    def appendCurrentLine(self, text: str):
        self.setText(self.toPlainText() + text)
        self.moveCursor(QtGui.QTextCursor.End)

    def setRawCurrentLine(self, text: str):
        before = self.toPlainText().split('\n')[:-1]
        before.append(f"{text}")
        self.setText("\n".join(before))
        self.moveCursor(QtGui.QTextCursor.End)

    def setCurrentLine(self, text: str):
        before = self.toPlainText().split('\n')[:-1]
        before.append(f"{TerminalEmulator.prompt}{text}")
        self.setText("\n".join(before))
        self.moveCursor(QtGui.QTextCursor.End)

    def currentLine(self):
        return self.toPlainText().split('\n')[-1][len(TerminalEmulator.prompt):]

    def appendLines(self, lines: List[str]):
        self.insertPlainText('\n'.join(lines))
        self.moveCursor(QtGui.QTextCursor.End)

    def appendText(self, text: str):
        self.insertPlainText(text)

    def appendHistory(self, command: str):
        if self.currentIndex != len(self.history):
            self.history.pop(self.currentIndex)
        self.history.append(command)
        self.currentIndex = len(self.history)

    def previousHistory(self) -> Union[str, None]:
        self.currentIndex -= 1
        if 0 <= self.currentIndex < len(self.history):
            return self.history[self.currentIndex]
        self.currentIndex += 1
        return None

    def nextHistory(self) -> Union[str, None]:
        self.currentIndex += 1
        if 0 <= self.currentIndex < len(self.history):
            return self.history[self.currentIndex]
        self.currentIndex -= 1
        return None

    def runCommand(self, command: str):
        sys.stdout = self
        sys.stderr = self
        self.interpreter.runsource(command)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.localsUpdated.emit(self.interpreter.locals)

    def isSelectionReadOnly(self) -> bool:
        cursor: QTextCursor = self.textCursor()
        start = cursor.selectionStart()

        if len(self.toPlainText()) - start > len(self.currentLine()):
            return True
        return False

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()

        # override keys
        # up and down
        if key == Qt.Key_Up:
            previous = self.previousHistory()
            if previous is None:
                return
            self.setCurrentLine(previous)
            return
        elif key == Qt.Key_Down:
            next = self.nextHistory()
            if next is None:
                return
            self.setCurrentLine(next)
            return
        # backspace
        if key == Qt.Key_Backspace:
            current = self.currentLine()
            if len(current) == 0:
                return
            if self.isSelectionReadOnly():
                self.setCurrentLine("")
                return
        # home
        if key == Qt.Key_Home:
            """
            how it works:
            >> something|
            |
            something|
            |something
            >> |something
            """
            current = self.currentLine()
            self.setRawCurrentLine("")
            self.appendText(current)
            self.moveCursor(QtGui.QTextCursor.StartOfLine)
            self.appendText(TerminalEmulator.prompt)
            return

        if key == Qt.Key_End:
            self.moveCursor(QtGui.QTextCursor.End)
            return

        shouldPress = False
        if key in TerminalEmulator.selectionWhiteListKeys:
            shouldPress = True

        modifiers = event.modifiers()
        if modifiers == Qt.ControlModifier or modifiers == Qt.AltModifier:
            shouldPress = True

        if not shouldPress and self.isSelectionReadOnly():
            return

        if key == Qt.Key_Return:
            line = self.currentLine()
            if line == TerminalEmulator.clearCommand:
                self.clear()
                self.setCurrentLine("")
                return

            super(TerminalEmulator, self).keyPressEvent(event)
            self.appendHistory(line)
            self.runCommand(line)
            self.setCurrentLine("")
            return

        super(TerminalEmulator, self).keyPressEvent(event)


class Display(QMainWindow):
    methodTree: QTreeView

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("WerryMath")
        self.resize(1200, 600)

        icon = QIcon("resources/icon.png")
        self.setWindowIcon(icon)

        self.console = TerminalEmulator()
        self.setCentralWidget(self.console)
        self.console.localsUpdated.connect(self.updateVariables)

        self.rightDock()
        self.bottomDock()

        self.setupRightDock()
        self.setupBottomDock()

    def updateFilter(self, newFilter):
        self.methodTreeFilter.setFilterRegExp(str(newFilter))
        if len(str(newFilter)) == 0:
            self.methodTree.expandToDepth(0)
        else:
            self.methodTree.expandAll()

    def handleImportModule(self):
        module = self.importLineEdit.text()
        self.console.importModule(module)
        self.importLineEdit.setText('')

    def rightDock(self):
        dock = QDockWidget("Methods", self)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setStyleSheet("""
                    QDockWidget {
                        titlebar-normal-icon: url(resources/dock/dock16.svg);
                    }
                """)
        vbox = QVBoxLayout()

        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Import:")
        self.importLineEdit = QLineEdit()
        self.importLineEdit.returnPressed.connect(self.handleImportModule)
        hbox.addWidget(label)
        hbox.addWidget(self.importLineEdit)
        widget = QWidget()
        widget.setLayout(hbox)
        vbox.addWidget(widget)

        self.methodTreeFilterLineEdit = QLineEdit()
        self.methodTreeFilterLineEdit.textChanged.connect(self.updateFilter)
        vbox.addWidget(self.methodTreeFilterLineEdit)
        self.methodTree = QTreeView(dock)
        self.methodTree.setHeaderHidden(True)
        vbox.addWidget(self.methodTree)
        widget = QWidget()
        widget.setLayout(vbox)
        dock.setWidget(widget)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def bottomDock(self):
        dock = QDockWidget("Variables", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        dock.setStyleSheet("""
            QDockWidget {
                titlebar-normal-icon: url(resources/dock/dock16.svg);
            }
        """)

        self.variableTable = QTableView(dock)
        self.variableTable.setSortingEnabled(True)
        dock.setWidget(self.variableTable)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def setupRightDock(self):
        # construct tree
        module_tree = self.constructModuleTree()
        self.model = module_tree.to_model()

        self.methodTreeFilter = CustomFilterModel()
        self.methodTreeFilter.setSourceModel(self.model)

        self.methodTree.setModel(self.methodTreeFilter)
        self.methodTree.doubleClicked.connect(self.methodTreeDoubleClicked)
        # self.methodTree.selectionModel().selectionChanged.connect(self.methodTreeSelectionChanged)
        self.methodTree.expandToDepth(0)

    def setupBottomDock(self):
        self.updateVariables({})

    def updateVariables(self, env: Dict[str, Optional[str]]):
        data = []
        empty = True
        for key in env:
            if key.startswith("__") and key.endswith("__"):
                continue
            val = env[key]
            if isinstance(val, ModuleType):
                continue

            try:
                module = val.__module__
                if module != '__console__':
                    continue
            except:
                pass

            data.append([type_to_str(env[key]), key, str(env[key])])
            empty = False

        if empty:
            data.append([])

        model = CustomTableModel(["Type", "Name", "Value"], data)
        self.variableTableFilter = CustomFilterModel()
        self.variableTableFilter.setSourceModel(model)
        self.variableTable.setModel(self.variableTableFilter)


    def methodTreeDoubleClicked(self, index: QModelIndex):
        model: QStandardItemModel = self.methodTree.model().sourceModel()
        item: CustomStandardItem = model.itemFromIndex(self.methodTreeFilter.mapToSource(index))
        if item is None or (not isinstance(item.node, Function) and not isinstance(item.node, Class)):
            return

        self.console.writeFunction(item.node)
        self.methodTree.setExpanded(index, not self.methodTree.isExpanded(index))


    def constructModuleTree(self) -> ModuleTree:
        moduleTree = ModuleTree()
        moduleTree.parse()
        return moduleTree


if __name__ == '__main__':
    app = QApplication(sys.argv)

    display = Display()
    display.show()

    # dark mode
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(85, 85, 85))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(51, 51, 51))
    dark_palette.setColor(QPalette.AlternateBase, QColor(65, 65, 65))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(85, 85, 85))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.white)
    app.setPalette(dark_palette)
    app.setStyleSheet("""
               QToolTip { 
                   color: #ffffff; 
                   background-color: #474747; 
                   border: 1px solid white;
               }
           """)

    sys.exit(app.exec_())
