import sys
import threading
from code import InteractiveConsole
from contextlib import contextmanager
from enum import Enum

from PyQt5.QtCore import *

from gui.hooks import ExceptionHooks
from utils.markers import Proxy, ProxyPackage


class TerminalWorkerStatus(Enum):
    running = "running"
    waiting = "waiting"


class TerminalWorkerSignals(QObject):
    started = pyqtSignal()
    running = pyqtSignal()
    waiting = pyqtSignal()
    finished = pyqtSignal(object)
    proxy = pyqtSignal(object)


class CustomConsole(InteractiveConsole):
    def __init__(self, onStart, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.onStart = onStart

    def raw_input(self, prompt=""):
        print(prompt, end='')
        self.raw_input = super(CustomConsole, self).raw_input
        self.onStart.emit()
        return input('')

    def runsource(self, source, filename="<input>", symbol="single"):
        ExceptionHooks().disable()
        super(CustomConsole, self).runsource(source, filename, symbol)
        ExceptionHooks().enable()


class TerminalWorker(QRunnable):
    # executing code
    interpreter: InteractiveConsole

    def __init__(self, newLine, *args, **kwargs):
        super(TerminalWorker, self).__init__(*args, **kwargs)

        self.event = threading.Event()
        self.signals = TerminalWorkerSignals()
        Proxy.proxy_fn = self.proxy
        self.interpreter = CustomConsole(self.signals.started)
        self.line = ""

        self.newLine = newLine

    def proxy(self, fn, args, kwargs):
        self.signals.proxy.emit(ProxyPackage(fn, args, kwargs))

    def locals(self):
        return self.interpreter.locals

    def run(self):
        sys.stdin = self
        sys.stdout = self
        sys.stderr = self
        try:
            self.interpreter.interact(banner="")
        except:
            pass

    def write(self, message: str):
        self.signals.finished.emit((message, self.interpreter.locals))

    def readline(self):
        self.signals.waiting.emit()
        with self.wait_signal(self.newLine):
            pass
        if self.line == 'quit()':
            raise Exception
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
