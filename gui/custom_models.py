"""
Custom Models for QViews
"""
from PyQt5.QtCore import QSortFilterProxyModel, QAbstractTableModel, QModelIndex, Qt
from typing import *

from PyQt5.QtGui import QPainter, QPalette, QColor
from PyQt5.QtWidgets import QTreeView, QStyleOptionViewItem


class CustomTree(QTreeView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filter = ""

    def drawRow(self, painter: QPainter, options: QStyleOptionViewItem, index: QModelIndex) -> None:
        model = self.model().sourceModel()
        item = model.itemFromIndex(self.model().mapToSource(index)).node
        if self.filter in item.name.lower() and len(self.filter) != 0:
            painter.fillRect(options.rect, QColor(22, 110, 228))
        super(CustomTree, self).drawRow(painter, options, index)

    def setFilter(self, newFilter: str):
        self.filter = newFilter.lower()


class CustomFilterModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        accept = super(CustomFilterModel, self).filterAcceptsRow(source_row, source_parent)
        if source_parent.row() == -1:
            return accept
        if accept:
            return True
        return self.filterAcceptsRow(source_parent.row(), source_parent.parent())


class CustomTableModel(QAbstractTableModel):
    def __init__(self, header: List[Any], data: List[List[Any]]):
        super(CustomTableModel, self).__init__()
        self.data = data
        self.header = header

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if role == Qt.DisplayRole:
            return self.data[index.row()][index.column()]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data[0])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self.header[section])
            else:
                return super(CustomTableModel, self).headerData(section, orientation, role)
