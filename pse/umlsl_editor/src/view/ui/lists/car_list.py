# controllers/car_list_controller.py
from PySide6.QtWidgets import QLabel, QPushButton # Assuming you have a database/list

from pse.umlsl_editor.src.view.ui.dialogs.car_edit_dialog import CarEditDialog
from pse.umlsl_editor.src.view.ui.lists.list_controller import ListController


class CarListController(ListController):
    def __init__(self, main_ui):
        # We configure the Base Class here
        super().__init__(
            main_ui=main_ui,
            list_widget_name="Cars",  # Specific UI ID
            edit_dialog_class=CarEditDialog  # Specific Dialog Class
        )

    def setup_row_ui(self, row_widget, car):
        pass