"""
List controller base class for the UMLSL Traffic Editor.

Provides base functionality for managing entity lists (cars, roads, queries).
"""
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Slot, QObject

from pse.umlsl_editor.src.view.ui_utils import load_ui
from pse.umlsl_editor.src.view.view_constants import UI_PATHS


class ListController(QObject):
    """
    Base controller for entity list widgets.

    Handles common list operations: refresh, add row, open editor.
    Subclasses must implement setup_row_ui() to populate row content.
    """

    def __init__(self, main_ui, list_widget_name: str, edit_dialog_class):
        """
        Initialize the list controller.

        Args:
            main_ui: Reference to the main UI widget.
            list_widget_name: Object name of the QListWidget in the UI.
            edit_dialog_class: Dialog class to use for editing items.
        """
        super().__init__()
        self.main_ui = main_ui
        self.list_widget = self.main_ui.findChild(QListWidget, list_widget_name)

        self.list_item_ui_path = UI_PATHS.LIST_ITEM
        self.EditDialogClass = edit_dialog_class

        self.refresh_list()

    def refresh_list(self) -> None:
        """Clear and rebuild the list from data source."""
        self.list_widget.clear()
        items = self.get_all_items()
        for item_data in items:
            self.add_row(item_data)

    def add_row(self, item_data) -> None:
        """
        Add a row widget for the given item data.

        Args:
            item_data: The entity data to display in the row.
        """
        row_widget = load_ui(self.list_item_ui_path)
        self.setup_row_ui(row_widget, item_data)

        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.setItemWidget(item, row_widget)

    @Slot()
    def open_editor(self, item_data) -> None:
        """
        Open the edit dialog for the given item.

        Args:
            item_data: The entity data to edit.
        """
        dialog = self.EditDialogClass(item_data, self)
        if dialog.exec():
            self.refresh_list()

    def get_all_items(self) -> list:
        """
        Get all items to display in the list.

        Must be implemented by subclasses.

        Returns:
            List of entity data objects.
        """
        raise NotImplementedError

    def setup_row_ui(self, row_widget, item_data) -> None:
        """
        Populate a row widget with item data.

        Must be implemented by subclasses.

        Args:
            row_widget: The widget for this row.
            item_data: The entity data to display.
        """
        raise NotImplementedError