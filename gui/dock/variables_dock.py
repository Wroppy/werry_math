from typing import Dict, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableView, QHeaderView

from gui.common import type_to_str
from gui.custom_items.custom_models import CustomTableModel, CustomFilterModel
from gui.dock.base_dock import BaseDock


class VariablesDock(BaseDock):
    variablesTableView: QTableView
    tableFilter: CustomFilterModel

    def __init__(self, display, *args):
        super().__init__(display, "Variable Table", *args)
        self.construct()
        self.set_default_layout()
        self.display.addDockWidget(Qt.BottomDockWidgetArea, self)
        self.setup()

    def construct(self):
        # create table
        self.variablesTableView = QTableView(self)
        self.variablesTableView.setSortingEnabled(True)

        # add to display
        self.setWidget(self.variablesTableView)

    def setup(self):
        self.display.console.localsChanged.connect(self.updateVariables)
        self.updateVariables({})

    def updateVariables(self, env: Dict[str, Optional[str]]):
        data = []
        for key in env:
            if key.startswith("__") and key.endswith("__"):
                continue
            data.append([type_to_str(type(env[key])), key, str(env[key])])

        if len(data) == 0:
            return

        model = CustomTableModel(["Type", "Name", "Value"], data)
        self.tableFilter = CustomFilterModel()
        self.tableFilter.setSourceModel(model)
        self.variablesTableView.setModel(self.tableFilter)
        self.variablesTableView.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
