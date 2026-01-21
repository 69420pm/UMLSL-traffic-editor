from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMainWindow, QDialog

from pse.umlsl_editor.src.view.ui.lists.edit_car_dialog import EditCarDialog
from pse.umlsl_editor.src.view.ui.lists.edit_query_dialog import EditQueryDialog
from pse.umlsl_editor.src.view.ui.lists.edit_road_dialog import EditRoadDialog
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class SidebarController(QObject):
    def __init__(self, main_window: Ui_MainWindow) -> None:
        super().__init__(main_window)
        self.window = main_window

        self.road_list_widget = self.window.l_roads
        self.car_list_widget = self.window.l_cars
        self.umlsl_query_list_widget = self.window.l_queries
        self.add_road_button = self.window.b_add_road
        self.add_car_button = self.window.b_add_car
        self.add_query_button = self.window.b_add_query

    def setup_ui(self) -> None:
        """Connect button click signals."""
        self.add_road_button.clicked.connect(lambda: self.open_edit_dialog(EditRoadDialog))
        self.add_car_button.clicked.connect(lambda: self.open_edit_dialog(EditCarDialog))
        self.add_query_button.clicked.connect(lambda: self.open_edit_dialog(EditQueryDialog))


    def open_edit_dialog(self, edit_dialog ) -> None:
        print("pressed")
        dialog = edit_dialog(self.window)
        dialog.exec()

