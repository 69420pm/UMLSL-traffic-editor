from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Slot

from pse.umlsl_editor.src.model.entities.road import RoadOrientation, Road
from pse.umlsl_editor.src.view.ui.lists.edit_road_dialog import EditRoadDialog
from pse.umlsl_editor.src.view.ui.lists.models.EntityModel import EntityModel

# 1. Define custom roles.
# These are the identifiers QML will use to ask for specific pieces of data.
NameRole = Qt.UserRole + 1
IconRole = Qt.UserRole + 2
ValueRole = Qt.UserRole + 3

class RoadModel(EntityModel):
    def __init__(self, roads: list[Road] | None, parent=None):
        super().__init__(parent)
        self._data = roads or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data for a specific row and role."""
        if not index.isValid():
            return None

        # Get the dictionary for the current row
        item = self._data[index.row()]
        is_vertical = item.orientation == RoadOrientation.VERTICAL

        if role == NameRole:
            return item.name
        elif role == IconRole:
            return is_vertical
        elif role == ValueRole:
            return ("x" if is_vertical else "y") + " = "  + str(item.position)

        return None

    def roleNames(self):
        """Maps the integer Role IDs to variable names used in QML."""
        return {
            NameRole: b"role_name",  # in QML: model.title
            IconRole: b"role_isRotated",  # in QML: model.status
            ValueRole: b"role_value",  # in QML: model.btnText
        }

    # ---------------------------------------------------------
    # Helper Methods for Interaction
    # ---------------------------------------------------------

    @Slot(int)
    def handle_button_click(self, row):
        EditRoadDialog(self._data[row]).exec_()