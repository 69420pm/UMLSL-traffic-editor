# pse/umlsl_editor/src/view/ui/lists/models/entity_list_model.py
from PySide6.QtCore import QAbstractListModel, QModelIndex, Slot, Qt

from pse.umlsl_editor.src.controllers.view_event_contract import ViewEventHandler
from pse.umlsl_editor.src.model.entities.entity import Entity


class EntityModel(QAbstractListModel):
    # 1. Define Base Roles
    IsSelectedRole = Qt.UserRole + 1

    # Helper for subclasses so they don't overwrite IDs
    NextRole = IsSelectedRole + 1

    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = []  # Single source of truth for data
        self._selected_uid = ""
        self._view_event_handler: ViewEventHandler | None = None

    def connect_sinal(self, view_event_handler):
        self._view_event_handler = view_event_handler
        self._view_event_handler.get_on_selection_changed_signal().connect(self.handle_selection_changed)

    # --- Common List Operations ---
    def add_entity(self, entity):
        if entity not in self._data:
            self.beginInsertRows(QModelIndex(), len(self._data), len(self._data))
            self._data.append(entity)
            self.endInsertRows()

    def remove_entity(self, entity):
        if entity in self._data:
            row = self._data.index(entity)
            self.beginRemoveRows(QModelIndex(), row, row)
            self._data.remove(entity)
            self.endRemoveRows()

    def update_entity(self, entity):
        if entity in self._data:
            row = self._data.index(entity)
            index = self.index(row)
            # Update all roles for this row
            self.dataChanged.emit(index, index, list(self.roleNames().keys()))

    def get_entity_at(self, row: int) -> Entity:
        return self._data[row]

    # --- Shared Data Logic ---
    def data(self, index, role=Qt.DisplayRole):
        """Handle the shared 'IsSelected' role here."""
        if not index.isValid():
            return None

        if role == EntityModel.IsSelectedRole:
            item = self._data[index.row()]
            return item.uid == self._selected_uid

        return None

    def roleNames(self):
        """Base roles that every list has."""
        return {
            EntityModel.IsSelectedRole: b"role_is_selected"
        }

    # --- Selection Handling ---
    @Slot(str)
    def handle_selection_changed(self, uid: str):
        """Called when the backend/global selection changes."""
        if self._selected_uid != uid:
            self._selected_uid = uid
            # Force the entire list to check for visual updates (background color)
            # (Optimized: You could calculate specific rows, but this is safer/easier)
            if self._data:
                self.dataChanged.emit(self.index(0), self.index(len(self._data) - 1), [EntityModel.IsSelectedRole])

    @Slot(int)
    def select_row(self, row):
        """Called by QML (ListRowDelegate) when clicked."""
        if 0 <= row < len(self._data):
            entity = self._data[row]
            self._view_event_handler.entity_selected_view(entity.uid)

    @Slot(int)
    def handle_button_click(self, row):
        pass
