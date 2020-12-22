from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from gui.common import WidgetHelper
from gui.custom_items.custom_models import CustomFilterModel
from gui.custom_items.custom_widgets import CustomTree
from gui.dock.base_dock import BaseDock
from gui.file_walker.module_tree import ModuleTree


class MethodsDock(BaseDock):
    methodsTreeView: CustomTree
    methodsTreeFilterModel: CustomFilterModel

    def __init__(self, display, *args):
        super(MethodsDock, self).__init__(display, "Method Tree", *args)
        self.construct()
        self.set_default_layout()
        self.display.addDockWidget(Qt.RightDockWidgetArea, self)
        self.setup()

    def setup(self):
        # setup tree
        moduleTree = ModuleTree(self.display.config.value('cdir'))
        moduleTree.parse()

        self.methodsTreeFilterModel = CustomFilterModel(parent=self.methodsTreeView)
        self.methodsTreeFilterModel.setSourceModel(moduleTree.to_model())

        self.methodsTreeView.setModel(self.methodsTreeFilterModel)
        self.methodsTreeView.doubleClicked.connect(self.handleTreeSelect)
        self.methodsTreeView.collapseAll()

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

        # add
        vbox = WidgetHelper.createVLayout(hbox, self.methodsTreeView)
        self.setWidget(vbox)

    def updateFilter(self, newFilter: str):
        self.methodsTreeView.clearSelection()
        newFilter = str(newFilter)
        self.methodsTreeView.setFilter(newFilter)
        self.methodsTreeFilterModel.setFilterRegExp(newFilter)
        if len(newFilter) == 0:
            self.methodsTreeView.collapseAll()
        else:
            self.methodsTreeView.expandAll()

    def handleReturn(self):
        indexes = self.methodsTreeView.highlighted_indexes
        if len(indexes) != 1:
            return

        index = indexes.__iter__().__next__()
        self.handleTreeSelect(index)

    def handleTreeSelect(self, index: QModelIndex):
        model: QStandardItemModel = self.methodsTreeView.model().sourceModel()
        item: QStandardItem = model.itemFromIndex(self.methodsTreeFilterModel.mapToSource(index))
        if item is None or not item.node.is_selectable():
            return

        self.display.console.writeFunction(item.node)
        self.methodsTreeView.setExpanded(index, not self.methodsTreeView.isExpanded(index))
