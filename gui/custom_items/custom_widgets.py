from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWidgets import QTreeView, QStyleOptionViewItem


class CustomTree(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter = ""
        self.highlighted_indexes = set()

    def drawRow(self, painter: QPainter, options: QStyleOptionViewItem, index: QModelIndex) -> None:
        model = self.model().sourceModel()
        item = model.itemFromIndex(self.model().mapToSource(index)).node
        if self.filter in item.name.lower() and len(self.filter) != 0:
            painter.fillRect(options.rect, QColor(22, 110, 228))
            self.highlighted_indexes.add(index)
        super(CustomTree, self).drawRow(painter, options, index)

    def setFilter(self, newFilter: str):
        self.filter = newFilter.lower()
        self.highlighted_indexes = set()