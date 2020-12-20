import os
import sys
import threading
from code import InteractiveConsole
from contextlib import contextmanager
from enum import Enum

from PyQt5.QtCore import *

from gui.exeception_hook import ExceptionHooks
from gui.message_handler import MessageHandler, MessageLevel


class ExitException(Exception):
    pass


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
        result = super().runsource(source, filename, symbol)
        ExceptionHooks().enable()
        return result


class TerminalWorker(QRunnable):
    # executing code
    interpreter: InteractiveConsole

    def __init__(self, newLine, *args, **kwargs):
        super(TerminalWorker, self).__init__(*args, **kwargs)

        self.event = threading.Event()
        self.signals = TerminalWorkerSignals()

        try:
            exec('from utilities.markers import Proxy')
            exec('Proxy.proxy_fn = self.proxy')
        except Exception as e:
            MessageHandler().emit(f"unable to import module 'Proxy': {repr(e)}", MessageLevel.WARNING)

        self.interpreter = CustomConsole(self.signals.started)
        self.line = ""
        self.newLine = newLine

    def proxy(self, fn, args, kwargs):
        try:
            exec('from utilities.markers import ProxyPackage')
            self.signals.proxy.emit(eval('ProxyPackage(fn, args, kwargs)'))
        except Exception as e:
            MessageHandler().emit(f"unable to import module 'ProxyPackage': {repr(e)}", MessageLevel.WARNING)

    def locals(self):
        return self.interpreter.locals

    def run(self):
        sys.stdin = self
        sys.stdout = self
        sys.stderr = self
        try:
            ExceptionHooks().add_hook(lambda *args: os._exit(1))
            self.interpreter.interact(banner="")
        except ExitException as e:
            MessageHandler().emit(f"exiting interpreter: {repr(e)}", MessageLevel.INFO)
        except Exception as e:
            MessageHandler().emit(f"exception in interpreter: {repr(e)}")
        MessageHandler().emit("interpreter stopped", MessageLevel.INFO)
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def write(self, message: str):
        self.signals.finished.emit((message, self.interpreter.locals))

    def readline(self):
        self.signals.waiting.emit()
        with self.wait_signal(self.newLine):
            pass
        if self.line == 'quit()':
            raise ExitException(f'received {self.line}')
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
