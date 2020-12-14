import math
import os
import sys
from abc import ABC, abstractmethod
from code import InteractiveInterpreter, InteractiveConsole
from contextlib import contextmanager
from enum import Enum
from typing import List, Union, Tuple

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui.hooks import ExceptionHooks
from gui.module_tree import Variable, Class, Function
from gui.resource_manager import ResourceManager
from gui.terminal.terminal_worker import TerminalWorker, TerminalWorkerStatus, ProxyPackage


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
        terminal.setText('')
        terminal.writeText(terminal.prompt)


class TerminalStatus(Enum):
    """
    Status of the terminal
    """
    waiting = 'waiting'
    executing = 'executing'
    readonly = 'readonly'


class TerminalEmulator(QTextEdit):
    """
    A customized python terminal emulator
    """
    # static stuff
    prompt: str = ">> "

    # instance variables
    history: List[str]
    historyIndex: int
    commands: List[TerminalCommand]
    status: TerminalStatus
    cursorIndex: int
    saved_line: str
    cmds = List[str]
    lines: List[str]
    fontSize: int
    worker: TerminalWorker

    # signals
    localsChanged: pyqtSignal = pyqtSignal(object)
    statusChanged: pyqtSignal = pyqtSignal(str)

    newLine: pyqtSignal = pyqtSignal(str)

    def __init__(self, welcome_message: str = None, cmds=None, *args, **kwargs):
        super(QTextEdit, self).__init__(*args, **kwargs)
        if cmds is None:
            self.cmds = []
        else:
            self.cmds = cmds

        self.setStyles()

        # setup instance variables
        self.commands = [ClearCommand()]
        self.history = []
        self.historyIndex = 0
        self.status = TerminalStatus.waiting
        self.cursorIndex = 0
        self.saved_line = ""
        self.lines = []

        worker = TerminalWorker(self.newLine)
        worker.signals.finished.connect(lambda message: self.handleWorkerStatus(TerminalWorkerStatus.waiting, message))
        worker.signals.running.connect(lambda: self.handleWorkerStatus(TerminalWorkerStatus.running))
        worker.signals.waiting.connect(lambda: self.handleWorkerStatus(TerminalWorkerStatus.waiting))
        worker.signals.started.connect(self.runCommands)
        worker.signals.proxy.connect(self.handleProxy)
        self.worker = worker
        QThreadPool().globalInstance().start(worker)

        if welcome_message is not None:
            self.writeText(welcome_message + "\n")
        self.setCurrentLine("")

        # connect
        self.selectionChanged.connect(self.handleSelectionChanged)

    def cleanUp(self):
        self.newLine.emit("quit()")

    def setStyles(self):
        self.fontSize = 12
        # styles
        font = ResourceManager.load_font("consolas/consolas.ttf")
        if font is not None:
            self.setFont(font)
            self.setFontSize(self.fontSize)
        self.setStyleSheet(ResourceManager.load_css("terminal.css"))

    def setFontSize(self, size: int):
        cursor = self.textCursor()
        self.selectAll()
        self.setFontPointSize(size)
        self.setTextCursor(cursor)

    # Selections #
    def handleSelectionChanged(self):
        if self.isSelectionReadOnly():
            self.setTerminalStatus(TerminalStatus.readonly)
        else:
            self.setTerminalStatus(TerminalStatus.waiting)

    def isSelectionReadOnly(self) -> bool:
        cursor: QTextCursor = self.textCursor()
        start = cursor.selectionStart()
        return len(self.toPlainText()) - start > len(self.currentLine())

    # Running Methods #
    def writeFunction(self, var: Variable):
        lcs = self.worker.locals()
        import_string, after = var.handleClicked(lcs)
        if import_string is not None:
            self.executeCommand(import_string, after)
        else:
            self.appendCurrentLine(after)
        self.setFocus()

    def executeCommand(self, command: str, after_execute: str = None):
        current_line = self.currentLine()
        self.setCurrentLine(command)
        self.keyPressEvent(QKeyEvent(QEvent.KeyPress, Qt.Key_Return, Qt.KeyboardModifiers()))
        if after_execute is not None:
            current_line += after_execute
        self.saved_line = current_line

    def executeCommands(self, commands: List[str], after_execute: str = None):
        current_line = self.currentLine()

        for command in commands:
            loop = QEventLoop()

            def stop(_):
                loop.quit()

            self.worker.signals.finished.connect(stop)
            self.executeCommand(command)
            with self.wait_signal(loop):
                pass
            self.worker.signals.finished.disconnect(stop)

        if after_execute is not None:
            current_line += after_execute
        self.saved_line = current_line

    def handleProxy(self, package: ProxyPackage):
        package.call()

    @contextmanager
    def wait_signal(self, loop):
        yield
        loop.exec_()

    # Line Manipulations #
    def appendCurrentLine(self, text: str):
        self.setText(self.toPlainText() + text)
        self.moveCursor(QTextCursor.End)

    def moveCursorToTheEnd(self):
        self.cursorIndex = len(self.toPlainText())
        self.moveCursor(QTextCursor.End)

    def setCurrentLine(self, text: str):
        before = self.toPlainText()[:self.cursorIndex]
        self.setText(before + text)
        self.moveCursor(QTextCursor.End)

    def currentLine(self):
        return self.toPlainText()[self.cursorIndex:]

    def writeText(self, text: str):
        self.insertPlainText(text)
        self.moveCursorToTheEnd()

    # History Management #
    def appendHistory(self, command: str):
        if self.historyIndex != len(self.history) and command == self.history[self.historyIndex]:
            self.history.pop(self.historyIndex)
        self.historyIndex = len(self.history)
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

    # Status Control #
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
            self.localsChanged.emit((variables))
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

    # Module Handling #
    def runCommands(self):
        self.executeCommands(self.cmds)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.ControlModifier:
            self.fontSize += math.copysign(1, event.angleDelta().y())
            self.setFontSize(self.fontSize)
        else:
            super(TerminalEmulator, self).wheelEvent(event)

    # Key Presses #
    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        modifiers = event.modifiers()

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
            if self.isSelectionReadOnly() or len(self.currentLine()) == 0:
                return

        # home and end
        if key == Qt.Key_Home:
            self.moveCursor(QTextCursor.End)
            cursor = self.textCursor()
            cursor.setPosition(self.cursorIndex, QTextCursor.MoveAnchor)
            self.setTextCursor(cursor)
            return
        if key == Qt.Key_End:
            self.moveCursor(QTextCursor.End)
            return

        # ctrl-A
        if modifiers == Qt.ControlModifier and key == Qt.Key_A:
            self.moveCursor(QTextCursor.End)
            cursor: QTextCursor = self.textCursor()
            cursor.setPosition(self.cursorIndex, QTextCursor.MoveAnchor)
            cursor.setPosition(self.cursorIndex + len(self.currentLine()), QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            return

        # other whitelists
        shouldPress = False
        if key in [Qt.Key_Left, Qt.Key_Right]:
            shouldPress = True

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
            self.appendHistory(line)
            self.lines.append(line)

            super(TerminalEmulator, self).keyPressEvent(event)
            if len(line) > 0 and line[0] == TerminalCommand.prefix:
                striped_line = line[len(TerminalCommand.prefix):]
                for command in self.commands:
                    if command.match(striped_line):
                        command.execute(self)
                        return

            self.newLine.emit(line)
            return

        super(TerminalEmulator, self).keyPressEvent(event)
