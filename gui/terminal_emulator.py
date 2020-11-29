import code
import sys
from enum import Enum
from typing import List, Union

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# QTextEdit but better
from gui.module_tree import Variable, Class, Function
from gui.resource_manager import ResourceManager


class TerminalStatus(Enum):
    idle = 'idle'
    executing = 'executing'
    readonly = 'readonly'


class TerminalEmulator(QTextEdit):
    prompt: str = ">> "
    clearCommand: str = "clear"
    selectionWhiteListKeys: List[Qt.Key] = [Qt.Key_Left, Qt.Key_Right]

    history: List[str]
    currentIndex: int

    interpreter: code.InteractiveInterpreter

    localsChanged: pyqtSignal = pyqtSignal(object)
    statusChanged: pyqtSignal = pyqtSignal(str)

    def __init__(self, welcome_message: str = None, *args, **kwargs):
        super(QTextEdit, self).__init__(*args, **kwargs)

        self.history = []
        self.currentIndex = 0

        self.lastStatus = TerminalStatus.idle

        self.interpreter = code.InteractiveInterpreter()

        # set font
        font = ResourceManager.load_font("consolas/consolas.ttf")
        if font is not None:
            self.setFont(font)

        self.setStyleSheet("""
            QTextEdit {
                background: #2e2e2e;
                color: #ddd;
                font-size: 16px;
            }
        """)

        if welcome_message is not None:
            self.setText(welcome_message + "\n")

        self.setCurrentLine("")
        self.selectionChanged.connect(self.handleSelectionChanged)

    def handleSelectionChanged(self):
        if self.isSelectionReadOnly():
            self.changeStatus(TerminalStatus.readonly)
        else:
            self.changeStatus(TerminalStatus.idle)

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
        self.moveCursor(QTextCursor.End)

    def setRawCurrentLine(self, text: str):
        before = self.toPlainText().split('\n')[:-1]
        before.append(f"{text}")
        self.setText("\n".join(before))
        self.moveCursor(QTextCursor.End)

    def setCurrentLine(self, text: str):
        before = self.toPlainText().split('\n')[:-1]
        before.append(f"{TerminalEmulator.prompt}{text}")
        self.setText("\n".join(before))
        self.moveCursor(QTextCursor.End)

    def currentLine(self):
        return self.toPlainText().split('\n')[-1][len(TerminalEmulator.prompt):]

    def appendLines(self, lines: List[str]):
        self.insertPlainText('\n'.join(lines))
        self.moveCursor(QTextCursor.End)

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

    def changeStatus(self, newStatus: TerminalStatus):
        if newStatus == self.lastStatus:
            return
        self.lastStatus = newStatus
        self.statusChanged.emit(str(newStatus.value))

    def runCommand(self, command: str):
        sys.stdout = self
        sys.stderr = self
        self.changeStatus(TerminalStatus.executing)
        self.interpreter.runsource(command)
        self.changeStatus(TerminalStatus.idle)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        self.localsChanged.emit(self.interpreter.locals)

    def isSelectionReadOnly(self) -> bool:
        cursor: QTextCursor = self.textCursor()
        start = cursor.selectionStart()

        if len(self.toPlainText()) - start > len(self.currentLine()):
            return True
        return False

    def keyPressEvent(self, event: QKeyEvent) -> None:
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
            self.moveCursor(QTextCursor.StartOfLine)
            self.appendText(TerminalEmulator.prompt)
            return

        if key == Qt.Key_End:
            self.moveCursor(QTextCursor.End)
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
