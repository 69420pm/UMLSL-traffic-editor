# controllers/base_list_controller.py
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget
from PySide6.QtCore import Slot, QObject  # Your helper function from before

from pse.umlsl_editor.src.view.ui_utils import load_ui


class ListController(QObject):
    def __init__(self, main_ui, list_widget_name, edit_dialog_class):
        super().__init__()
        self.main_ui = main_ui
        self.list_widget = self.main_ui.findChild(QListWidget, list_widget_name)

        # Store configuration
        self.list_item_ui_path = "ui/list.ui"
        self.EditDialogClass = edit_dialog_class  # We pass the CLASS itself, not an instance

        self.refresh_list()

    def refresh_list(self):
        """Standard logic to clear and rebuild the list."""
        self.list_widget.clear()
        items = self.get_all_items()  # Abstract method: Child must implement this
        for item_data in items:
            self.add_row(item_data)

    def add_row(self, item_data):
        """Standard logic to load a row widget and add it to the list."""
        row_widget = load_ui(self.list_item_ui_path)

        # Hook for child classes to fill data (text, colors, etc.)
        self.setup_row_ui(row_widget, item_data)

        # Standard list insertion
        item = QListWidgetItem(self.list_widget)
        item.setSizeHint(row_widget.sizeHint())
        self.list_widget.setItemWidget(item, row_widget)

    @Slot()
    def open_editor(self, item_data):
        """Opens the dialog class provided in __init__."""
        # Initialize the dialog class passed in the constructor
        dialog = self.EditDialogClass(item_data, self)
        if dialog.exec():
            self.refresh_list()

    def setup_row_ui(self, row_widget, item_data):
        raise NotImplementedError