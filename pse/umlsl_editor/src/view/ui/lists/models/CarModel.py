from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Slot

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation, Road
from pse.umlsl_editor.src.view.ui.lists.edit_car_dialog import EditCarDialog
from pse.umlsl_editor.src.view.ui.lists.models.EntityModel import EntityModel

# 1. Define custom roles.
# These are the identifiers QML will use to ask for specific pieces of data.
NameRole = Qt.UserRole + 1
IconRole = Qt.UserRole + 2
ValueRole = Qt.UserRole + 3

class CarModel(EntityModel):
    def __init__(self, cars: list[Car] | None, parent=None):
        super().__init__(parent)
        self._data = cars or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data for a specific row and role."""
        if not index.isValid():
            return None

        # Get the dictionary for the current row
        item = self._data[index.row()]

        if role == NameRole:
            return item.name
        elif role == IconRole:
            return True
        elif role == ValueRole:
            return item.position_on_lane

        return None

    def roleNames(self):
        """Maps the integer Role IDs to variable names used in QML."""
        return {
            NameRole: b"role_name",  # in QML: model.title
            IconRole: b"role_isRotated",  # in QML: model.status
            ValueRole: b"role_value",  # in QML: model.btnText
        }

    @Slot(int)
    def handle_button_click(self, row):
        EditCarDialog(self._data[row]).exec_()