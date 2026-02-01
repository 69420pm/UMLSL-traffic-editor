from PySide6.QtCore import Qt, QModelIndex, Slot

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.view.ui.lists.edit_car_dialog import EditCarDialog
from pse.umlsl_editor.src.view.ui.lists.models.entity_model import EntityModel

# 1. Define custom roles.
# These are the identifiers QML will use to ask for specific pieces of data.
NameRole = Qt.UserRole + 1
ColorRole = Qt.UserRole + 2
ValueRole = Qt.UserRole + 3


class CarModel(EntityModel):
    def __init__(self, cars: list["Car"] | None, parent=None):
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
        elif role == ValueRole:
            return "R: " + item.lane.road_uid + "L: " + str(item.lane.lane_index)
        elif role == ColorRole:
            return item.color

        return None

    def roleNames(self):
        """Maps the integer Role IDs to variable names used in QML."""
        return {
            NameRole: b"role_name",
            ColorRole: b"role_color",
            ValueRole: b"role_value",
        }

    @Slot(int)
    def handle_button_click(self, row):
        EditCarDialog(self._data[row]).exec_()
