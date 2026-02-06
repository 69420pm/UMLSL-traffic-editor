"""
Base entity list model for the UMLSL Traffic Editor.

Provides an abstract base class for QML list models that display selectable
entity collections. Handles common functionality including selection state
management and row operations.
"""

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt, QTimer, Signal, Slot

from pse.umlsl_editor.src.controllers.view_event_contract import ViewEventHandler
from pse.umlsl_editor.src.model.entities.entity import Entity


class EntityModel(QAbstractListModel):
    """
    Abstract base class for entity list models.

    Provides common functionality for list models that display selectable
    entities in QML views. Subclasses should define additional roles for
    entity-specific properties.

    Features:
        - Selection state tracking and synchronization
        - Entity add/remove/update operations
        - Base role for selection state exposed to QML

    Attributes:
        IsSelectedRole: Role ID for the selection state.
        NextRole: Starting role ID for subclass-defined roles.
    """

    IsSelectedRole = Qt.UserRole + 1
    NextRole = IsSelectedRole + 1

    edit_requested = Signal(int)  # Emits row index when edit is requested

    def __init__(self, parent=None) -> None:
        """
        Initialize the entity model.

        Args:
            parent: The parent QObject. Defaults to None.
        """
        super().__init__(parent)
        self._data: list[Entity] = []
        self._selected_uid: str = ""
        self._view_event_handler: ViewEventHandler | None = None

    def connect_signal(self, view_event_handler: ViewEventHandler) -> None:
        """
        Connect to the view event handler for selection synchronization.

        Args:
            view_event_handler: The handler providing selection change signals.
        """
        self._view_event_handler = view_event_handler
        selection_signal = self._view_event_handler.get_on_selection_changed_signal()
        selection_signal.connect(self._handle_selection_changed)

    # -------------------------------------------------------------------------
    # Entity Operations
    # -------------------------------------------------------------------------

    def add_entity(self, entity: Entity) -> None:
        """
        Add an entity to the model.

        Args:
            entity: The entity to add.
        """
        if entity in self._data:
            return

        row = len(self._data)
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.append(entity)
        self.endInsertRows()

    def remove_entity(self, entity: Entity) -> None:
        """
        Remove an entity from the model.

        Defers removal to the next event loop iteration to prevent
        conflicts with QML signal handlers that may be in progress.

        Args:
            entity: The entity to remove.
        """
        if entity not in self._data:
            return

        # Defer removal to next event loop iteration to avoid destroying
        # objects while QML signal handlers are still in progress.
        QTimer.singleShot(0, lambda: self._do_remove_entity(entity))

    def _do_remove_entity(self, entity: Entity) -> None:
        """
        Perform the actual entity removal.

        Args:
            entity: The entity to remove.
        """
        if entity not in self._data:
            return

        row = self._data.index(entity)
        self.beginRemoveRows(QModelIndex(), row, row)
        self._data.remove(entity)
        self.endRemoveRows()

    def clear_all(self) -> None:
        """
        Remove all entities from the model in a single reset.
        """
        if not self._data:
            return

        self.beginResetModel()
        self._data.clear()
        self._selected_uid = ""
        self.endResetModel()

    def update_entity(self, entity: Entity) -> None:
        """
        Notify that an entity's data has changed.

        Args:
            entity: The entity that was updated.
        """
        if entity not in self._data:
            return

        row = self._data.index(entity)
        index = self.index(row)
        self.dataChanged.emit(index, index, list(self.roleNames().keys()))

    def get_entity_at(self, row: int) -> Entity:
        """
        Get the entity at the specified row index.

        Args:
            row: The row index.

        Returns:
            The entity at the given row.
        """
        return self._data[row]

    # -------------------------------------------------------------------------
    # QAbstractListModel Implementation
    # -------------------------------------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Return the number of rows in the model.

        Args:
            parent: The parent index (unused for flat lists).

        Returns:
            The number of entities in the model.
        """
        return len(self._data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        """
        Return data for the specified index and role.

        Handles the IsSelectedRole for selection state. Subclasses should
        call super().data() first and handle additional roles if None is returned.

        Args:
            index: The model index.
            role: The data role to retrieve.

        Returns:
            The data for the role, or None if not applicable.
        """
        if not index.isValid():
            return None

        if role == EntityModel.IsSelectedRole:
            entity = self._data[index.row()]
            return entity.uid == self._selected_uid

        return None

    def roleNames(self) -> dict[int, bytes]:
        """
        Return the role names mapping for QML access.

        Subclasses should call super().roleNames() and update with additional roles.

        Returns:
            Dictionary mapping role IDs to QML property names.
        """
        return {
            EntityModel.IsSelectedRole: b"role_is_selected",
        }

    # -------------------------------------------------------------------------
    # Selection Handling
    # -------------------------------------------------------------------------

    @Slot(str)
    def _handle_selection_changed(self, uid: str) -> None:
        """
        Handle global selection change events.

        Updates the selected UID and emits dataChanged for all rows to
        refresh selection state display.

        Args:
            uid: The UID of the newly selected entity.
        """
        if self._selected_uid == uid:
            return

        self._selected_uid = uid

        if self._data:
            first_index = self.index(0)
            last_index = self.index(len(self._data) - 1)
            self.dataChanged.emit(first_index, last_index, [EntityModel.IsSelectedRole])

    @Slot(int)
    def select_row(self, row: int) -> None:
        """
        Handle row selection from QML.

        Called when a list row is clicked in the UI. Notifies the view
        event handler of the selection.

        Args:
            row: The index of the selected row.
        """
        if not (0 <= row < len(self._data)):
            return

        entity = self._data[row]
        if self._view_event_handler:
            self._view_event_handler.entity_selected_view(entity.uid)

    @Slot(int)
    def handle_button_click(self, row: int) -> None:
        """
        Handle button click for a specific row.

        Emits the edit_requested signal with the row index. Connect to this
        signal to open an edit dialog with the appropriate parent widget.

        Args:
            row: The index of the row whose button was clicked.
        """
        if 0 <= row < len(self._data):
            self.edit_requested.emit(row)
