import os
from types import ModuleType
from typing import Dict, Optional

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from gui.common import type_to_str
from gui.custom_models import CustomFilterModel, CustomTableModel
from gui.resource_manager import ResourceManager
from gui.terminal_emulator import TerminalEmulator, TerminalStatus
from gui.module_tree import CustomStandardItem, Function, ModuleTree, Class

cdir = os.path.dirname(os.path.realpath(__file__))


class Display(QMainWindow):
    methodTree: QTreeView

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("WerryMath")
        self.resize(1200, 600)

        icon = ResourceManager.load_icon("app/icon.png")
        self.setWindowIcon(icon)

        vbox = QVBoxLayout()
        self.console = TerminalEmulator("Started Python Interpreter")
        vbox.addWidget(self.console)
        self.console_status = QLabel(str(TerminalStatus.idle.value))
        self.console_status.setAlignment(Qt.AlignRight)
        vbox.addWidget(self.console_status)
        widget = QWidget()
        widget.setLayout(vbox)
        self.setCentralWidget(widget)
        self.console.localsChanged.connect(self.updateVariables)
        self.console.statusChanged.connect(self.updateStatus)
        self.rightDock()
        self.bottomDock()

        self.setupRightDock()
        self.setupBottomDock()

    def updateStatus(self, newStatus: str):
        self.console_status.setText(newStatus)

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
        moduleTree = ModuleTree(cdir)
        moduleTree.parse()
        return moduleTree


if __name__ == '__main__':
    app = QApplication(sys.argv)

    display = Display()
    display.show()

    app.setStyle("Fusion")

    font = ResourceManager.load_font("roboto/Roboto-Regular.ttf")
    if font is not None:
        app.setFont(font)

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
    app.setStyleSheet(f"""
               QToolTip {{ 
                   color: #ffffff; 
                   background-color: #474747; 
                   border: 1px solid white;
               }}
               * {{
                    font-size: 14px;
               }}
               QDockWidget {{
                    titlebar-normal-icon: url({ResourceManager.get_resource_url("dock/dock16.svg")});
               }}
               QDockWidget::title {{
                   background-color: #24292b;
                   padding: 6px;
                   margin: 0;
               }} 
           """)

    sys.exit(app.exec_())
