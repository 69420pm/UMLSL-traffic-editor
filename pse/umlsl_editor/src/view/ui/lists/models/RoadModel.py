from PySide6.QtCore import QAbstractListModel, Qt, QModelIndex, Slot

from pse.umlsl_editor.src.model.entities.road import RoadOrientation, Road

# 1. Define custom roles.
# These are the identifiers QML will use to ask for specific pieces of data.
NameRole = Qt.UserRole + 1
IconRole = Qt.UserRole + 2
ValueRole = Qt.UserRole + 3

class RoadModel(QAbstractListModel):
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

        if role == NameRole:
            return item.name
        elif role == IconRole:
            return item.orientation == RoadOrientation.VERTICAL
        elif role == ValueRole:
            return item.position

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
    def handleButtonClick(self, row):
        """Called from QML when a button is clicked."""
        if 0 <= row < len(self._data):
            item = self._data[row]
            print(f"[Python] Action triggered for: {item.name}")


    @Slot(int)
    def removeItem(self, row):
        """Call this from QML to delete a tile."""
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._data[row]
        self.endRemoveRows()