"""
Editor dialog base controller for the UMLSL Traffic Editor.

Provides a base class for entity editing dialogs (cars, roads, queries).
"""
from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot

from pse.umlsl_editor.src.view.ui_utils import load_ui


class EditDialog:
    """
    Base class for entity editing dialogs.

    Provides common functionality for loading UI, connecting buttons,
    and handling save/delete operations. Subclasses must implement
    load_data_into_ui() and get_data_from_ui().
    """

    def __init__(self, item_data, controller, ui_path: str):
        """
        Initialize the edit dialog.

        Args:
            item_data: The entity data to edit.
            controller: The controller handling updates and deletions.
            ui_path: Path to the .ui file for this dialog.
        """
        self.item_data = item_data
        self.controller = controller
        self.ui_path = ui_path

        self.setup_ui()

    def setup_ui(self) -> None:
        """Load the UI file and connect standard buttons."""
        self.widget = load_ui(self.ui_path)

        # Find standard buttons (naming convention: b_save, b_delete)
        self.btn_save = self.widget.findChild(QPushButton, "b_save")
        self.btn_delete = self.widget.findChild(QPushButton, "b_delete")

        if self.btn_save:
            self.btn_save.clicked.connect(self.on_save)
        if self.btn_delete:
            self.btn_delete.clicked.connect(self.on_delete)

        self.load_data_into_ui()

    def exec(self) -> int:
        """
        Execute the dialog modally.

        Returns:
            The dialog result code.
        """
        return self.widget.exec()

    @Slot()
    def on_save(self) -> None:
        """Handle save button click: validate, update, and close."""
        updated_item = self.get_data_from_ui()
        if updated_item:
            self.controller.handle_update(updated_item)
            self.widget.accept()

    @Slot()
    def on_delete(self) -> None:
        """Handle delete button click: delete and close."""
        self.controller.handle_delete(self.item_data)
        self.widget.reject()

    def load_data_into_ui(self) -> None:
        """
        Populate UI fields with item data.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    def get_data_from_ui(self):
        """
        Read UI fields and create an updated entity.

        Must be implemented by subclasses.

        Returns:
            The updated entity, or None if validation fails.
        """
        raise NotImplementedError