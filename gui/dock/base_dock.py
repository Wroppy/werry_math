from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class BaseDock(QDockWidget):
    display: 'display.Display'
    name: str

    def __init__(self, display: 'display.Display', name: str, *args):
        super(BaseDock, self).__init__(name, *args)
        self.display = display
        self.name = name

    def set_default_layout(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)

    def construct(self):
        pass

    def setup(self):
        pass
