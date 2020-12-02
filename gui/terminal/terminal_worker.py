import sys
import threading
from code import InteractiveConsole
from contextlib import contextmanager
from enum import Enum
from time import sleep
from typing import List

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class TerminalWorkerStatus(Enum):
    running = "running"
    waiting = "waiting"


class TerminalWorkerSignals(QObject):
    started = pyqtSignal()
    running = pyqtSignal()
    waiting = pyqtSignal()
    finished = pyqtSignal(object)


class CustomConsole(InteractiveConsole):
    def __init__(self, onStart, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onStart = onStart

    def raw_input(self, prompt=""):
        print(prompt, end='')
        self.raw_input = super(CustomConsole, self).raw_input
        self.onStart.emit()
        return input('')


class TerminalWorker(QRunnable):
    # executing code
    interpreter: InteractiveConsole

    def __init__(self, newLine, *args, **kwargs):
        super(TerminalWorker, self).__init__(*args, **kwargs)

        self.event = threading.Event()
        self.signals = TerminalWorkerSignals()
        self.interpreter = CustomConsole(self.signals.started)
        self.line = ""

        self.newLine = newLine

    def run(self):
        exception = None
        sys.stdin = self
        sys.stdout = self
        sys.stderr = self
        try:
            self.interpreter.interact(banner="")
        except Exception as e:
            exception = e
            sys.stdin = sys.__stdin__
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        finally:
            if exception is not None:
                print(exception)

    def write(self, message: str):
        self.signals.finished.emit((message, self.interpreter.locals))

    def readline(self):
        self.signals.waiting.emit()
        with self.wait_signal(self.newLine):
            pass
        self.signals.running.emit()
        if self.line == '':
            self.line = '\n'
        return self.line

    @contextmanager
    def wait_signal(self, signal):
        loop = QEventLoop()

        def stop(message):
            self.line = message
            loop.quit()

        signal.connect(stop)

        yield

        loop.exec_()
