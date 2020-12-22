from PyQt5.QtWidgets import *

from display import Display


class BaseDock(QDockWidget):
    display: Display
    name: str

    def __init__(self, display: Display, name: str, *args):
        super(BaseDock, self).__init__(*args)
        self.display = display
        self.name = name
