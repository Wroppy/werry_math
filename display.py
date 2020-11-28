import code
import inspect
import os
from abc import ABC, abstractmethod
from typing import List, Union, Any, Callable

from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

cdir = os.path.dirname(os.path.realpath(__file__))


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


# Do more than just functions thou
class Function(TreeNode):
    def __init__(self, parent: TreeNode, name: str, fn: Callable):
        self.parent = parent
        self.name = name
        self.fn = fn
        self.path = os.path.join(parent.path, name)

    def parse(self):
        pass

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, self.name)
        return item

    def to_import_path(self) -> str:
        return ".".join(
            os.path.join(self.parent.path[:-len(ModuleTree.file_extension)], self.name)[len(cdir) + 1:].split(
                os.path.sep))


class Module(TreeNode):
    nodes: List[TreeNode]

    def __init__(self, parent: TreeNode, name: str):
        self.nodes = []
        self.parent = parent
        self.name = name
        self.path = os.path.join(parent.path, name)

    def parse(self):
        import importlib.util
        name = self.name[:-len(ModuleTree.file_extension)]
        spec = importlib.util.spec_from_file_location(name, self.path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        methods = list(filter(lambda m: not m[0].startswith("__"), inspect.getmembers(module, inspect.isfunction)))
        for fn_name, fn_callable in methods:
            fn = Function(self, fn_name, fn_callable)
            self.nodes.append(fn)

    def to_model(self) -> CustomStandardItem:
        item = CustomStandardItem(self, self.name)
        for node in self.nodes:
            item.appendRow(node.to_model())
        return item


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
        item = CustomStandardItem(self, self.name)
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

    history: List[str]
    current_index: int

    interpreter: code.InteractiveInterpreter

    def __init__(self, *args, **kwargs):
        super(QTextEdit, self).__init__(*args, **kwargs)

        self.history = []
        self.current_index = 0

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

    def writeFunction(self, fn: Function):
        import_path = fn.to_import_path()
        root = import_path.split('.')[0]
        if fn.name not in self.interpreter.locals:
            if root not in self.interpreter.locals:
                self.importModule(root)
            else:
                self.appendCurrentLine(f"{import_path}")
                self.setFocus()
                return
        self.appendCurrentLine(fn.name)
        self.setFocus()

    def executeCommand(self, command: str):
        current_line = self.currentLine()
        self.setCurrentLine(command)
        self.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifiers()))
        self.setCurrentLine(current_line)

    def appendCurrentLine(self, text: str):
        self.setText(self.toPlainText() + text)
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

    def appendHistory(self, command: str):
        if self.current_index != len(self.history):
            self.history.pop(self.current_index)
        self.history.append(command)
        self.current_index = len(self.history)

    def previousHistory(self) -> Union[str, None]:
        self.current_index -= 1
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        self.current_index += 1
        return None

    def nextHistory(self) -> Union[str, None]:
        self.current_index += 1
        if 0 <= self.current_index < len(self.history):
            return self.history[self.current_index]
        self.current_index -= 1
        return None

    def runCommand(self, command: str):
        sys.stdout = self
        sys.stderr = self
        self.interpreter.runsource(command)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def isSelectionReadOnly(self) -> bool:
        cursor: QTextCursor = self.textCursor()
        start = cursor.selectionStart()

        if len(self.toPlainText()) - start > len(self.currentLine()):
            return True
        return False

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()

        # history
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

        if self.isSelectionReadOnly() and not (key == Qt.Key_Left or key == Qt.Key_Right):
            return

        # return
        if key == Qt.Key_Return:
            line = self.currentLine()
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

        self.rightDock()
        self.bottomDock()

        self.setupRightDock()

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
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
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
        self.variableTable = QTableView(dock)
        dock.setWidget(self.variableTable)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    def setupRightDock(self):
        # construct tree
        module_tree = self.constructModuleTree()
        self.model = module_tree.to_model()

        self.methodTreeFilter = CustomFilterModel()
        self.methodTreeFilter.setSourceModel(self.model)

        self.methodTree.setModel(self.methodTreeFilter)
        self.methodTree.selectionModel().selectionChanged.connect(self.methodTreeSelectionChanged)
        self.methodTree.expandToDepth(0)

    def updateVariables(self, variables):
        # implement the variables
        pass

    def methodTreeSelectionChanged(self, event: QItemSelection):
        if event.isEmpty():
            return
        selected: QItemSelectionRange = event.first()
        index: QModelIndex = selected.indexes()[0]
        model: QStandardItemModel = self.methodTree.model().sourceModel()
        item: CustomStandardItem = model.itemFromIndex(self.methodTreeFilter.mapToSource(index))
        if item is None or not isinstance(item.node, Function):
            return

        self.console.writeFunction(item.node)
        self.methodTree.selectionModel().clearSelection()

    def constructModuleTree(self) -> ModuleTree:
        moduleTree = ModuleTree()
        moduleTree.parse()
        return moduleTree


if __name__ == '__main__':
    app = QApplication(sys.argv)

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
                background-color: #2a82da; 
                border: 1px solid white; 
            }
        """)

    display = Display()
    display.show()

    sys.exit(app.exec_())
