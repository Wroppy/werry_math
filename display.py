import os
import sys
import subprocess

from typing import Dict, Optional, List

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from cli.cli_parser import CLIParser
from gui.common import WidgetHelper
from gui.config.display_config import DisplayConfig, DisplayHelper
from gui.display_bundle import DisplayBundle
from gui.dock.base_dock import BaseDock
from gui.dock.methods_dock import MethodsDock
from gui.dock.variables_dock import VariablesDock
from gui.exeception_hook import ExceptionHooks
from gui.message_handler import MessageHandler, MessageLevel
from gui.resource_manager import ResourceManager
from gui.terminal.terminal_emulator import TerminalEmulator, TerminalStatus



class Display(QMainWindow):
    """
    The Display class handles displaying the gui
    It contains all the docks and widgets
    """

    # widgets----------------
    docks: List[BaseDock]

    # parser----------------
    # CLIParser ignored flags
    ignoredModules = ["cdir", "spath"]
    # used to represent the current script directory
    cdir: str
    # used to represent the history bundle save path
    spath: str

    # ----------------

    config: DisplayConfig

    def __init__(self, config: DisplayConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

        # window frame setup
        self.setWindowTitle("WerryMath")
        self.resize(1200, 600)

        # set icon
        icon = ResourceManager.load_icon("app/icon_trans.png")
        self.setWindowIcon(icon)

        # set current dir
        self.cdir = config.value_or_default('cdir', lambda:os.path.dirname(os.path.realpath(__file__)))

        # set save dir
        self.spath = config.value_or_default('spath', lambda: os.path.join(os.path.dirname(os.path.realpath(__file__)), 'commands'))

        # setup console and status
        self.console = TerminalEmulator("Started Python Interpreter", config.imports())
        self.console_status = QLabel(str(TerminalStatus.waiting.value))
        self.console_status.setAlignment(Qt.AlignRight)
        vbox = WidgetHelper.createVLayout(self.console, self.console_status)
        self.setCentralWidget(vbox)

        # bind console
        self.console.statusChanged.connect(self.updateStatus)

        # create docks
        self.create_docks()

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
        bundle.set('history', self.console.lines[len(self.console.cmds):])
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

    def updateStatus(self, newStatus: str):
        self.console_status.setText(newStatus)

    def create_docks(self):
        self.docks = [MethodsDock(self), VariablesDock(self)]

    # unused
    def createLeftDock(self):
        # TODO: Abstract dock creation
        pass
        # dock = self.createDock('Canvas')
        #
        # label = QLabel()
        # canvas = QPixmap(400, 400)
        # canvas.fill(Qt.white)
        # label.setPixmap(canvas)
        # with open('data.csv', 'r+') as f:
        #      import csv
        #      reader = csv.reader(f)
        #      i = 1
        #
        #      for row in reader:
        #          x = row[0]
        #          z = row[2]
        #
        #          painter = QPainter(label.pixmap())
        #          pen = QPen()
        #          pen.setWidth(i)
        #          if i > 10:
        #              break
        #          i += 0.01
        #          painter.setPen(pen)
        #          painter.drawPoint(200+float(x)*200, 200-float(z)*200)
        #          painter.end()
        #
        #
        # label.update()
        #
        # dock.setWidget(label)
        # self.addDockWidget(Qt.LeftDockWidgetArea, dock)


    def setupLeftDock(self):
        pass



def pre_app():
    # fix windows icon not displaying
    if sys.platform == "win32":
        import ctypes
        appid = "com.troppydash.werry_math"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

    # set current directory as path
    currentDir = os.path.dirname(os.path.realpath(__file__))
    sys.path.insert(0, os.path.realpath(currentDir))

    # add python if exists
    pythonlib_paths = []
    if sys.platform == "win32":
        python_path = subprocess.check_output("python -c \"import sys;print(sys.path)\"", shell=True).strip()
        python_path = python_path.decode('utf-8')
        if r'Microsoft\WindowsApps' not in python_path:
            try:
                paths = eval(python_path)
                paths = filter(lambda x: len(x) > 0, paths)
                pythonlib_paths.extend(paths)
            except Exception as e:
                MessageHandler().emit(str(e))
        MessageHandler().emit(f"found python with: {python_path}", MessageLevel.DEBUG)
    else:
        MessageHandler().emit(f"unable to import python on current platform {sys.platform}")

    if len(pythonlib_paths) != 0:
        for path in pythonlib_paths:
            if path not in sys.path:
                sys.path.append(path)
    MessageHandler().emit(str(sys.path), MessageLevel.DEBUG)

    # register exception hook
    ExceptionHooks().add_hook(lambda *a, **k: QApplication.quit())


def post_app(app: QApplication):
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    if hasattr(QStyleFactory, 'AA_UseHighDpiPixmaps'):
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)

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
    p = CLIParser(sys.argv[1:], DisplayHelper())
    config = DisplayConfig(p)

    value = config.value('lvl')
    if value:
        level = MessageLevel.from_str(value)
        MessageHandler(level).emit(f"message handler started with level: {value}", MessageLevel.INFO)

    pre_app()
    app = QApplication(sys.argv)
    post_app(app)

    display = Display(config)

    code = app.exec_()
    MessageHandler().emit(f"application finished with code {code}", MessageLevel.INFO)
    sys.exit(code)
