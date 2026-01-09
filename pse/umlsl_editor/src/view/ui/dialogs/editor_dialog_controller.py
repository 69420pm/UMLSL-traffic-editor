from PySide6.QtWidgets import QDialog, QPushButton
from PySide6.QtCore import Slot

from pse.umlsl_editor.src.view.ui_utils import load_ui


class EditDialog:

    def __init__(self, item_data, controller, ui_path: str):
        self.item_data = item_data
        self.controller = controller
        self.ui_path = ui_path

        self.setup_ui()

    def setup_ui(self) -> None:
        # 1. Load the specific UI file
        self.widget = load_ui(self.ui_path)

        # 2. Find standard buttons (Enforce naming convention in Designer!)
        self.btn_save = self.widget.findChild(QPushButton, "b_save")
        self.btn_delete = self.widget.findChild(QPushButton, "b_delete")

        # 3. Connect buttons
        if self.btn_save:
            self.btn_save.clicked.connect(self.on_save)
        if self.btn_delete:
            self.btn_delete.clicked.connect(self.on_delete)

        # 4. Fill the fields (Abstract method)
        self.load_data_into_ui()

    def exec(self) -> int:
        """Wraps the QDialog exec method."""
        return self.widget.exec()

    @Slot()
    def on_save(self) -> None:
        """
        1. Reads data from UI (Child must implement this)
        2. Sends update to controller
        3. Closes window
        """
        updated_item = self.get_data_from_ui()  # Calls child method
        if updated_item:
            # We assume the controller has an 'update_item' or generic method
            # Or we specifically call a method on the controller if we know the type
            self.controller.handle_update(updated_item)
            self.widget.accept()

    @Slot()
    def on_delete(self) -> None:
        """Standard delete logic"""
        self.controller.handle_delete(self.item_data)
        self.widget.reject()

    # --- Abstract Methods (Children MUST implement these) ---
    def load_data_into_ui(self) -> None:
        """Take self.item_data and put it into QLineEdits"""
        raise NotImplementedError

    def get_data_from_ui(self):
        """Read QLineEdits and return a new Object (Car/Road)"""
        raise NotImplementedError