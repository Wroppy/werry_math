from PyQt5.QtCore import QSortFilterProxyModel, QAbstractTableModel, QModelIndex, Qt
from typing import *


class CustomFilterModel(QSortFilterProxyModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRecursiveFilteringEnabled(True)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)


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

