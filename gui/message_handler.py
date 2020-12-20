import sys
from enum import Enum
from typing import List, Optional

from gui.common import singleton


class MessageLevel(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2  # default
    ERROR = 3

    def __str__(self):
        if self == MessageLevel.DEBUG:
            return "DEBUG"
        elif self == MessageLevel.INFO:
            return "INFO"
        elif self == MessageLevel.WARNING:
            return "WARNING"
        elif self == MessageLevel.ERROR:
            return "ERROR"
        raise Exception

    @staticmethod
    def from_str(level: str) -> Optional['MessageLevel']:
        level = level.upper()
        if level == 'DEBUG':
            return MessageLevel.DEBUG
        elif level == 'INFO':
            return MessageLevel.INFO
        elif level == 'WARNING':
            return MessageLevel.WARNING
        elif level == 'ERROR':
            return MessageLevel.ERROR

        return None


@singleton
class MessageHandler:
    def __init__(self, levelFilter: MessageLevel = None):
        if levelFilter is None:
            levelFilter = MessageLevel.WARNING
        self.levelFilter = levelFilter

    def emit(self, message: str, level: MessageLevel = MessageLevel.WARNING):
        if self.levelFilter.value > level.value:
            return
        MessageHandler.log(f"[{level}] {message}")

    def emitList(self, messages: List[str], level: MessageLevel = MessageLevel.INFO):
        if self.levelFilter.value > level.value:
            return
        for message in messages:
            MessageHandler.log(f"[{level}] {message}")

    @staticmethod
    def log(message: str):
        old_out = sys.stdout
        old_err = sys.stderr

        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        print(message)

        sys.stdout = old_out
        sys.stderr = old_err
