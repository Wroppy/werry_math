import sys
from code import InteractiveConsole

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TerminalWorkerSignals(QObject):
    waiting = pyqtSignal(object)
    finished = pyqtSignal(object)


class TerminalWorker(QRunnable):

    # executing code
    interpreter: InteractiveConsole

    def __init__(self, *args, **kwargs):
        super(TerminalWorker, self).__init__(*args, **kwargs)

        self.interpreter = InteractiveConsole()
        sys.stdin = self
        sys.stdout = self
        sys.stderr = self

    # overrides
    def write(self, message: str):
        self.appendLines(message.split('\n'))

    def clear(self):
        self.setText("")

    def readline(self):
        return "input not supported yet"