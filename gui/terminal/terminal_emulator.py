import os
import sys
from abc import ABC, abstractmethod
from code import InteractiveInterpreter, InteractiveConsole
from enum import Enum
from typing import List, Union, Tuple

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui.module_tree import Variable, Class, Function
from gui.resource_manager import ResourceManager
from gui.terminal.terminal_worker import TerminalWorker, TerminalWorkerStatus


class TerminalCommand(ABC):
    prefix = "!"

    @abstractmethod
    def match(self, line: str) -> bool:
        pass

    @abstractmethod
    def execute(self, terminal: 'TerminalEmulator'):
        pass


class ClearCommand(TerminalCommand):
    def match(self, line: str) -> bool:
        return line == 'clear'

    def execute(self, terminal: 'TerminalEmulator'):
        pass


class TerminalStatus(Enum):
    """
    Status of the terminal
    """
    waiting = 'waiting'
    executing = 'executing'
    readonly = 'readonly'


class TerminalEmulator(QTextEdit):
    # static stuff
    prompt: str = ">> "

    # instance variables
    history: List[str]
    historyIndex: int
    commands: List[TerminalCommand]
    status: TerminalStatus
    cursorIndex: int
    saved_line: str
    modules = List[str]

    # signals
    localsChanged: pyqtSignal = pyqtSignal(object)
    statusChanged: pyqtSignal = pyqtSignal(str)

    newLine: pyqtSignal = pyqtSignal(str)

    def __init__(self, welcome_message: str = None, *args, **kwargs):
        super(QTextEdit, self).__init__(*args, **kwargs)

        self.setStyles()

        # setup instance variables
        self.commands = [ClearCommand()]
        self.history = []
        self.historyIndex = 0
        self.status = TerminalStatus.waiting
        self.interpreter = InteractiveConsole()
        self.cursorIndex = 0
        self.saved_line = ""
        self.modules = []

        self.threadPool = QThreadPool()
        worker = TerminalWorker(self.newLine)
        worker.signals.finished.connect(lambda message: self.handleWorkerStatus(TerminalWorkerStatus.waiting, message))
        worker.signals.running.connect(lambda: self.handleWorkerStatus(TerminalWorkerStatus.running))
        worker.signals.waiting.connect(lambda: self.handleWorkerStatus(TerminalWorkerStatus.waiting))
        worker.signals.started.connect(self.loadModules)
        self.threadPool.start(worker)

        if welcome_message is not None:
            self.writeText(welcome_message + "\n")
        self.setCurrentLine("")

        # connect
        self.selectionChanged.connect(self.handleSelectionChanged)


    def setStyles(self):
        # styles
        font = ResourceManager.load_font("consolas/consolas.ttf")
        if font is not None:
            self.setFont(font)
        self.setStyleSheet(ResourceManager.load_css("terminal.css"))

    def handleSelectionChanged(self):
        if self.isSelectionReadOnly():
            self.setTerminalStatus(TerminalStatus.readonly)
        else:
            self.setTerminalStatus(TerminalStatus.waiting)

    def isSelectionReadOnly(self) -> bool:
        cursor: QTextCursor = self.textCursor()
        start = cursor.selectionStart()
        return len(self.toPlainText()) - start > len(self.currentLine())

    def writeFunction(self, var: Variable):
        import_path = var.to_import_path()
        root = import_path.split('.')[0]
        if isinstance(var, Class) or (isinstance(var, Function) and not var.method):
            if var.name not in self.interpreter.locals:
                if root not in self.interpreter.locals:
                    self.executeCommand(f"from {root} import *", var.to_console_str())
                else:
                    self.appendCurrentLine(f"{import_path}")

        self.setFocus()

    def executeCommand(self, command: str, after_execute: str = None):
        current_line = self.currentLine()
        self.setCurrentLine(command)
        self.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifiers()))
        if after_execute is not None:
            current_line += after_execute
        self.saved_line = current_line

    # Line Manipulations #
    def appendCurrentLine(self, text: str):
        self.setText(self.toPlainText() + text)
        self.moveCursor(QTextCursor.End)

    def moveCursorToTheEnd(self):
        self.cursorIndex = len(self.toPlainText())
        self.moveCursor(QTextCursor.End)

    def setCurrentLine(self, text: str):
        before = self.toPlainText()[:self.cursorIndex]
        self.setText(before+text)
        self.moveCursor(QTextCursor.End)

    def currentLine(self):
        return self.toPlainText()[self.cursorIndex:]

    def writeText(self, text: str):
        self.insertPlainText(text)
        self.moveCursorToTheEnd()

    # History Management #
    def appendHistory(self, command: str):
        if self.historyIndex != len(self.history):
            self.history.pop(self.historyIndex)
        self.history.append(command)
        self.historyIndex = len(self.history)

    def previousHistory(self) -> Union[str, None]:
        self.historyIndex -= 1
        if 0 <= self.historyIndex < len(self.history):
            return self.history[self.historyIndex]
        self.historyIndex += 1
        return None

    def nextHistory(self) -> Union[str, None]:
        self.historyIndex += 1
        if 0 <= self.historyIndex < len(self.history):
            return self.history[self.historyIndex]
        self.historyIndex -= 1
        return None

    # status control
    def setTerminalStatus(self, newStatus: TerminalStatus):
        if newStatus == self.status:
            return
        if self.status == TerminalStatus.executing and newStatus != TerminalStatus.waiting:
            return
        self.status = newStatus
        self.statusChanged.emit(str(newStatus.value))

    def writeResult(self, result: Tuple[str, object]):
        display, variables = result
        is_prompt = False
        if display == '>>> ':
            is_prompt = True
            display = TerminalEmulator.prompt
            self.localsChanged.emit(variables)
        self.writeText(display)
        if is_prompt:
            if len(self.saved_line) != 0:
                self.appendCurrentLine(self.saved_line)
                self.saved_line = ""

    def handleWorkerStatus(self, newStatus: TerminalWorkerStatus, result=None):
        if newStatus == TerminalWorkerStatus.waiting:
            self.setTerminalStatus(TerminalStatus.waiting)
            if result is not None:
                self.writeResult(result)
        elif newStatus == TerminalWorkerStatus.running:
            self.setTerminalStatus(TerminalStatus.executing)

    def appendModule(self, module: str):
        self.modules.append(module)

    def loadModules(self):
        # this is annoying without a delay
        for module in self.modules:
            self.executeCommand(module)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()

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
            if self.isSelectionReadOnly():
                return

        # home and end
        if key == Qt.Key_Home:
            self.moveCursor(QTextCursor.End)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, len(self.currentLine()))
            self.setTextCursor(cursor)
            return
        if key == Qt.Key_End:
            self.moveCursor(QTextCursor.End)
            return

        # other whitelists
        shouldPress = False
        if key in [Qt.Key_Left, Qt.Key_Right]:
            shouldPress = True

        modifiers = event.modifiers()
        if modifiers == Qt.ControlModifier:
            if not (key == Qt.Key_V and self.isSelectionReadOnly()):
                shouldPress = True
        elif modifiers == Qt.AltModifier:
            shouldPress = True

        if not shouldPress and self.isSelectionReadOnly():
            return

        # enter
        if key == Qt.Key_Return:
            self.moveCursor(QTextCursor.End)
            line = self.currentLine()
            super(TerminalEmulator, self).keyPressEvent(event)
            self.appendHistory(line)
            self.newLine.emit(line)
            return

        super(TerminalEmulator, self).keyPressEvent(event)
