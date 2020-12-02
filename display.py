import os
from types import ModuleType
from typing import Dict, Optional, List

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from cli.cli_parser import CLIParser
from gui.common import type_to_str
from gui.custom_models import CustomFilterModel, CustomTableModel
from gui.resource_manager import ResourceManager
from gui.terminal.terminal_emulator import TerminalEmulator, TerminalStatus
from gui.module_tree import CustomStandardItem, Function, ModuleTree, Class


class Display(QMainWindow):
    methodTree: QTreeView

    # static vars
    ignoredModules = ["cdir"]

    def __init__(self, parser: CLIParser, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # window frame setup
        self.setWindowTitle("WerryMath")
        self.resize(1200, 600)

        # set icon
        icon = ResourceManager.load_icon("app/icon_trans.png")
        self.setWindowIcon(icon)

        # parse args
        parser.parse(Display.ignoredModules)

        # set current dir
        flag, ok = parser.contains("cdir")
        if ok and flag.has_value():
            self.cdir = flag.value
        else:
            self.cdir = os.path.dirname(os.path.realpath(__file__))
        # setup console
        self.console = TerminalEmulator("Started Python Interpreter")
        self.console_status = QLabel(str(TerminalStatus.waiting.value))
        self.console_status.setAlignment(Qt.AlignRight)
        vbox = Display.createVLayout(self.console, self.console_status)
        self.setCentralWidget(vbox)

        # bind console
        self.console.localsChanged.connect(self.updateVariables)
        self.console.statusChanged.connect(self.updateStatus)

        # create docks
        self.createLeftDock()
        self.createRightDock()
        self.createBottomDock()

        # setup docks
        self.setupRightDock()
        self.setupBottomDock()
        self.setupLeftDock()

        self.importModules(parser.imports())

    def importModules(self, import_str: List[str]):
        for string in import_str:
            self.console.appendModule(string)

    def createDock(self, *args, **kwargs) -> QDockWidget:
        dock = QDockWidget(*args, **kwargs, parent=self)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setStyleSheet(
            ResourceManager.load_css_with_var("dock.css",
                                              ("icon()", ResourceManager.get_resource_url("icon", "dock/dock16.svg")))
        )
        return dock

    @staticmethod
    def createVLayout(*args: QWidget, vbox: QVBoxLayout = None) -> QWidget:
        if vbox is None:
            vbox = QVBoxLayout()
        for widget in args:
            vbox.addWidget(widget)
        w = QWidget()
        w.setLayout(vbox)
        return w

    @staticmethod
    def createHLayout(*args: QWidget, hbox: QHBoxLayout = None) -> QWidget:
        if hbox is None:
            hbox = QHBoxLayout()
        for widget in args:
            hbox.addWidget(widget)
        w = QWidget()
        w.setLayout(hbox)
        return w

    def updateStatus(self, newStatus: str):
        self.console_status.setText(newStatus)

    def updateFilter(self, newFilter: str):
        self.methodTreeFilter.setFilterRegExp(str(newFilter))
        if len(str(newFilter)) == 0:
            self.methodTree.expandToDepth(0)
        else:
            self.methodTree.expandAll()

    def handleTreeSelect(self, index: QModelIndex):
        model: QStandardItemModel = self.methodTree.model().sourceModel()
        item: CustomStandardItem = model.itemFromIndex(self.methodTreeFilter.mapToSource(index))
        if item is None or (not isinstance(item.node, Function) and not isinstance(item.node, Class)):
            return

        self.console.writeFunction(item.node)
        self.methodTree.setExpanded(index, not self.methodTree.isExpanded(index))

    # dock creations
    def createLeftDock(self):
        dock = self.createDock("Helpers")
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

    def createRightDock(self):
        dock = self.createDock("Methods")

        # create filter
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Search")
        self.methodTreeFilterLineEdit = QLineEdit()
        self.methodTreeFilterLineEdit.textChanged.connect(self.updateFilter)
        hbox = Display.createHLayout(label, self.methodTreeFilterLineEdit, hbox=hbox)

        # create tree
        self.methodTree = QTreeView(dock)
        self.methodTree.setHeaderHidden(True)

        # add to display
        vbox = Display.createVLayout(hbox, self.methodTree)
        dock.setWidget(vbox)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)

    def createBottomDock(self):
        dock = self.createDock("Variables")

        # create table
        self.variableTable = QTableView(dock)
        self.variableTable.setSortingEnabled(True)

        # add to display
        dock.setWidget(self.variableTable)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)

    # dock setups
    def setupRightDock(self):
        # setup tree
        moduleTree = ModuleTree(self.cdir)
        moduleTree.parse()
        self.model = moduleTree.to_model()

        self.methodTreeFilter = CustomFilterModel()
        self.methodTreeFilter.setSourceModel(self.model)

        self.methodTree.setModel(self.methodTreeFilter)
        self.methodTree.doubleClicked.connect(self.handleTreeSelect)
        self.methodTree.expandToDepth(0)

    def setupBottomDock(self):
        # init variables
        self.updateVariables({})

    def setupLeftDock(self):
        pass

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


def pre_display():
    # fix windows icon not displaying
    if sys.platform == "win32":
        import ctypes
        appid = "com.troppydash.werry_math"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    # hidpi
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)


def post_display(app: QApplication):
    # custom style
    app.setStyle("Fusion")

    # custom font
    font = ResourceManager.load_font("roboto/Roboto-Regular.ttf")
    if font is not None:
        app.setFont(font)

    # dark mode
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
    # custom styles
    app.setStyleSheet(ResourceManager.load_css("display.css"))


if __name__ == '__main__':
    pre_display()

    app = QApplication(sys.argv)

    p = CLIParser(sys.argv[1:])
    display = Display(p)

    post_display(app)
    display.show()

    try:
        code = app.exec_()
    except Exception as e:
        print(e)
    sys.exit(code)
