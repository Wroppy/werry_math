import os
from typing import Dict, Optional, List

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys

from cli.cli_parser import CLIParser
from gui.common import type_to_str
from gui.custom_models import CustomFilterModel, CustomTableModel
from gui.display_bundle import DisplayBundle
from gui.hooks import ExceptionHooks
from gui.resource_manager import ResourceManager
from gui.terminal.terminal_emulator import TerminalEmulator, TerminalStatus
from gui.module_tree import CustomStandardItem, Function, ModuleTree, Class


class Display(QMainWindow):
    """
    The Display class handles displaying the gui
    It contains all the docks and widgets
    """

    # widgets----------------
    # right dock tree view instance
    methodsTreeView: QTreeView
    # right dock widget
    rightDockWidget: QDockWidget
    # bottom dock widget
    bottomDockWidget: QDockWidget
    # table widget view
    variablesTableView: QTableView
    # custom filtering model
    methodsTreeFilterModel: CustomFilterModel
    # ----------------

    # parser----------------
    # CLIParser ignored flags
    ignoredModules = ["cdir", "spath"]
    # used to represent the current script directory
    cdir: str
    # used to represent the history bundle save path
    spath: str

    # ----------------

    def __init__(self, parser: CLIParser, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # window frame setup
        self.setWindowTitle("WerryMath")
        self.resize(1200, 600)

        # set icon
        icon = ResourceManager.load_icon("app/icon_trans.png")
        self.setWindowIcon(icon)

        # parse arguments
        parser.parse(Display.ignoredModules)

        # set current dir
        flag, ok = parser.contains("cdir")
        if ok and flag.has_value():
            self.cdir = flag.value
        else:
            self.cdir = os.path.dirname(os.path.realpath(__file__))

        # set save dir
        flag, ok = parser.contains("spath")
        if ok and flag.has_value():
            self.spath = flag.value
        else:
            self.spath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'commands')

        # setup console and status
        self.console = TerminalEmulator("Started Python Interpreter", parser.imports())
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

        self.show()

        bundle = self.load()
        if bundle is not None:
            self.attempt_load(bundle)

    def to_display_bundle(self):
        """
        create a bundle with the display's state
        :return:
        """
        bundle = DisplayBundle()
        bundle.set('history', self.console.lines)
        return bundle

    def save(self):
        bundle = self.to_display_bundle()
        bundle.dump(self.spath)

    def load(self) -> Optional[DisplayBundle]:
        return DisplayBundle.load(self.spath)

    def attempt_load(self, bundle):
        reply = QMessageBox.question(self, 'Message', f'Load bundle from {self.spath}{DisplayBundle.ext}?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        history = bundle.get('history')
        self.console.executeCommands(history)

    def attempt_save(self):
        reply = QMessageBox.question(self, 'Message', f'Save bundle to {self.spath}{DisplayBundle.ext}?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save()

    def closeEvent(self, event):
        self.attempt_save()
        self.console.cleanUp()
        super(Display, self).closeEvent(event)

    def createDock(self, *args) -> QDockWidget:
        dock = QDockWidget(*args, parent=self)
        dock.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
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
        self.methodsTreeFilterModel.setFilterRegExp(str(newFilter))
        if len(str(newFilter)) == 0:
            self.methodsTreeView.expandToDepth(0)
        else:
            self.methodsTreeView.expandAll()

    def handleTreeSelect(self, index: QModelIndex):
        model: QStandardItemModel = self.methodsTreeView.model().sourceModel()
        item: CustomStandardItem = model.itemFromIndex(self.methodsTreeFilterModel.mapToSource(index))
        if item is None or (not isinstance(item.node, Function) and not isinstance(item.node, Class)):
            return

        self.console.writeFunction(item.node)
        self.methodsTreeView.setExpanded(index, not self.methodsTreeView.isExpanded(index))

    # dock creations
    def createLeftDock(self):
        pass

    def createRightDock(self):
        dock = self.createDock("Methods")

        # create filter input
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Search")
        lineEdit = QLineEdit()
        lineEdit.textChanged.connect(self.updateFilter)
        hbox = Display.createHLayout(label, lineEdit, hbox=hbox)

        # create tree
        self.methodsTreeView = QTreeView(dock)
        self.methodsTreeView.setHeaderHidden(True)

        # add to display
        vbox = Display.createVLayout(hbox, self.methodsTreeView)
        dock.setWidget(vbox)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        self.rightDockWidget = dock

    def createBottomDock(self):
        dock = self.createDock("Variables")

        # create table
        self.variablesTableView = QTableView(dock)
        self.variablesTableView.setSortingEnabled(True)

        # add to display
        dock.setWidget(self.variablesTableView)
        self.addDockWidget(Qt.BottomDockWidgetArea, dock)
        self.bottomDockWidget = dock

    # dock setups
    def setupRightDock(self):

        # setup tree
        moduleTree = ModuleTree(self.cdir)
        moduleTree.parse()

        self.methodsTreeFilterModel = CustomFilterModel()
        self.methodsTreeFilterModel.setSourceModel(moduleTree.to_model())

        self.methodsTreeView.setModel(self.methodsTreeFilterModel)
        self.methodsTreeView.doubleClicked.connect(self.handleTreeSelect)
        self.methodsTreeView.expandToDepth(0)

    def setupBottomDock(self):
        # init variables
        self.updateVariables({})

    def setupLeftDock(self):
        pass

    def updateVariables(self, env: Dict[str, Optional[str]]):
        data = []
        for key in env:
            if key.startswith("__") and key.endswith("__"):
                continue
            data.append([type_to_str(type(env[key])), key, str(env[key])])

        if len(data) == 0:
            return

        model = CustomTableModel(["Type", "Name", "Value"], data)
        tableFilter = CustomFilterModel()
        tableFilter.setSourceModel(model)
        self.variablesTableView.setModel(tableFilter)


def pre_display():
    # fix windows icon not displaying
    if sys.platform == "win32":
        import ctypes
        appid = "com.troppydash.werry_math"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    # hidpi
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

    # set path
    old = sys.path.pop()
    currentDir = os.path.dirname(os.path.realpath(__file__))
    sys.path.append(os.path.realpath(currentDir))
    sys.path.append(old)


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
    app.setStyleSheet(ResourceManager.join_css(
        ResourceManager.load_css("display.css"),
        ResourceManager.load_css_with_var("dock.css",
                                          ("icon()", ResourceManager.get_resource_url("icon", "dock/dock64.svg")))
    ))


if __name__ == '__main__':
    ExceptionHooks().add_hook(lambda *a, **k: QApplication.quit())

    pre_display()

    app = QApplication(sys.argv)

    post_display(app)

    p = CLIParser(sys.argv[1:])

    display = Display(p)
    sys.exit(app.exec_())
