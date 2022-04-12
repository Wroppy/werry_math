import os
import sys
import subprocess

from typing import Optional, List

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from cli.cli_parser import CLIParser
from gui.common import WidgetHelper
from gui.config.display_config import DisplayConfig, DisplayHelper
from gui.display_bundle import DisplayBundle
from gui.dock.base_dock import BaseDock
from gui.dock.methods_dock import MethodsDock
from gui.dock.variables_dock import VariablesDock
from gui.exeception_hook import ExceptionHooks
from gui.message_handler import MessageHandler, MessageLevel
from gui.path_handler import PathHandler
from gui.resource_manager import ResourceManager
from gui.splash_screen import SplashScreen
from gui.terminal.terminal_emulator import TerminalEmulator, TerminalStatus
# from gui.titlebar import WindowWithTitlebar


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

    # ----------------

    config: DisplayConfig

    def __init__(self, config: DisplayConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config

        # window frame setup
        self.setWindowTitle("WerryMath")
        self.resize(1200, 600)

        SplashScreen().displayMessage("parsing arguments")

        # set icon
        icon = ResourceManager.load_icon("app/icon_trans.png")
        self.setWindowIcon(icon)

        # set current dir
        if os.path.isdir('scripts'):
            config.value_or_default('cdir', lambda: 'scripts')
        else:
            config.value_or_default('cdir', lambda: os.path.dirname(os.path.realpath(__file__)))
        PathHandler().add_to_path(config.value('cdir'))
        # set save dir
        config.value_or_default('spath', lambda: os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                              'commands'))

        SplashScreen().displayMessage("setting up the console")
        # setup console and status
        self.console = TerminalEmulator("Started Python Interpreter", config.imports())
        self.console_status = QLabel(str(TerminalStatus.waiting.value))
        self.console_status.setAlignment(Qt.AlignRight)
        vbox = WidgetHelper.createVLayout(self.console, self.console_status)
        self.setCentralWidget(vbox)

        # bind console
        self.console.statusChanged.connect(self.updateStatus)

        SplashScreen().displayMessage("creating docks")
        # create docks
        self.create_docks()

        SplashScreen().displayMessage("starting display")
        self.show()
        SplashScreen().finish(self)

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
        bundle.dump(self.config.value('spath'))

    def load(self) -> Optional[DisplayBundle]:
        return DisplayBundle.load(self.config.value('spath'))

    def attempt_load(self, bundle):
        reply = QMessageBox.question(self, 'Message',
                                     f'Load bundle from {self.config.value("spath")}{DisplayBundle.ext}?',
                                     QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        history = bundle.get('history')
        self.console.executeCommands(history)

    def attempt_save(self):
        reply = QMessageBox.question(self, 'Message',
                                     f'Save bundle to {self.config.value("spath")}{DisplayBundle.ext}?',
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
    # sys.path.insert(0, os.path.realpath(currentDir))

    # add python if exists
    pythonlib_paths = []
    try:
        if sys.platform == "win32":
            python_path = subprocess.check_output("python -c \"import sys;print(sys.path)\"", shell=True).strip()
            python_path = python_path.decode('utf-8')
            if r'Microsoft\WindowsApps' not in python_path:
                paths = eval(python_path)
                paths = filter(lambda x: len(x) > 0, paths)
                pythonlib_paths.extend(paths)
                MessageHandler().emit(f"found python with: {python_path}", MessageLevel.DEBUG)
            else:
                MessageHandler().emit(f"found msstore python, please use another version of python", MessageLevel.DEBUG)
        else:
            python_path = subprocess.check_output('python3 -c \"import sys;print(sys.path)\"', shell=True).strip()
            python_path = python_path.decode('utf-8')
            paths = eval(python_path)
            paths = filter(lambda x: len(x) > 0, paths)
            pythonlib_paths.extend(paths)
            MessageHandler().emit(f"found python with: {paths}", MessageLevel.DEBUG)
    except Exception as e:
        MessageHandler().emit(str(e))

    if len(pythonlib_paths) == 0:
        MessageHandler().emit(f"unable to import python on current platform {sys.platform}")

    # include base zip
    if os.path.exists('pythonlib.zip'):
        MessageHandler().emit(f"found pythonlib.zip", MessageLevel.DEBUG)
        PathHandler().insert_to_path(os.path.join(currentDir, 'pythonlib.zip'))

    # add to path
    for path in pythonlib_paths:
        PathHandler().add_to_path(path)

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

    # custom styles
    app.setStyleSheet(ResourceManager.join_css(
        ResourceManager.load_css("display.css"),
        ResourceManager.load_css_with_var("dock.css",
                                          ("icon()", ResourceManager.get_resource_url("icon", "dock/dock64.svg")))
    ))
    # light mode
    if sys.platform == 'win32':
        settings = QSettings(r"HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                             QSettings.NativeFormat)
        if settings.value("AppsUseLightTheme") == 1:
            return

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


if __name__ == '__main__':
    # parser config and help messages
    p = CLIParser(sys.argv[1:], DisplayHelper())

    # create display config
    config = DisplayConfig(p)

    # set logging level
    value = config.value('lvl')
    if value:
        level = MessageLevel.from_str(value)
        MessageHandler(level).emit(f"message handler started with level: {value}", MessageLevel.INFO)

    # add imports and sys.path
    pre_app()
    app = QApplication(sys.argv)

    # create splash screen
    splash = SplashScreen()
    splash.show()

    SplashScreen().displayMessage("loading styles")
    # set styling
    post_app(app)

    # start display
    display = Display(config)

    # event loop
    code = app.exec_()
    MessageHandler().emit(f"application finished with code {code}", MessageLevel.INFO)
    sys.exit(code)


# TODO: make the save file a history and a copy of local variables, and no prompt but a clear button