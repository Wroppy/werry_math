from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui.common import WidgetHelper
from gui.custom_items.custom_widgets import CustomTree
from gui.dock.base_dock import BaseDock


class TreeDock(BaseDock):
    methodsTreeView: CustomTree

    def __init__(self, display, *args):
        super(TreeDock, self).__init__(display, "MethodTree", *args)
        self.setup()
        self.construct()

    def setup(self):
        self.setFeatures(QDockWidget.DockWidgetFloatable | QDockWidget.DockWidgetMovable)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.BottomDockWidgetArea | Qt.RightDockWidgetArea)
        self.display.addDockWidget(Qt.RightDockWidgetArea, self)

    def construct(self):
        # create filter input
        hbox = QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Search")
        lineEdit = QLineEdit()
        lineEdit.textChanged.connect(self.updateFilter)
        lineEdit.returnPressed.connect(self.handleReturn)
        hbox = WidgetHelper.createHLayout(label, lineEdit, hbox=hbox)

        # create tree
        self.methodsTreeView = CustomTree(self)
        self.methodsTreeView.setHeaderHidden(True)


    def updateFilter(self, newFilter: str):
        self.methodsTreeView.clearSelection()
        newFilter = str(newFilter)
        self.methodsTreeView.setFilter(newFilter)
        self.methodsTreeFilterModel.setFilterRegExp(newFilter)
        if len(newFilter) == 0:
            self.methodsTreeView.collapseAll()
        else:
            self.methodsTreeView.expandAll()
