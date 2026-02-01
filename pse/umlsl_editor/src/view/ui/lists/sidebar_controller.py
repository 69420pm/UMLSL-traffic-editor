import os

from PySide6.QtCore import QObject, QUrl, Qt

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.lists.edit_road_dialog import EditRoadDialog
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class SidebarController(QObject):
    def __init__(self, main_window: Ui_MainWindow, application_controller: ApplicationController) -> None:
        super().__init__(main_window)
        self._view_models = application_controller.view_event_handler.view_models
        self._application_controller = application_controller
        self._window = main_window

        self._road_quick_widget = self._window.q_roads
        self._car_quick_widget = self._window.q_cars
        self._query_quick_widget = self._window.q_queries

        self._add_road_button = self._window.b_add_road
        self._add_car_button = self._window.b_add_car
        self._add_query_button = self._window.b_add_query

        self.setup_ui()

    def setup_ui(self) -> None:
        """Connect button click signals."""
        self._add_road_button.clicked.connect(lambda: self.open_edit_dialog(EditRoadDialog))

        # self._add_car_button.clicked.connect(lambda: self.open_edit_dialog(EditQueryDialog))
        # self._add_query_button.clicked.connect(lambda: self.open_edit_dialog(EditQueryDialog))

        def setup_quick_widget(quick_widget, model, qml_file_path: str) -> None:
            """Set up a QML Quick Widget with the given model and QML file."""
            quick_widget.setClearColor(Qt.transparent)
            quick_widget.setAttribute(Qt.WA_TranslucentBackground)
            quick_widget.setAttribute(Qt.WA_AlwaysStackOnTop)
            quick_widget.setResizeMode(quick_widget.ResizeMode.SizeRootObjectToView)

            quick_widget.rootContext().setContextProperty("data_model", model)
            quick_widget.setSource(QUrl.fromLocalFile(qml_file_path))

        base_dir = os.path.dirname(os.path.abspath(__file__))
        qml_folder = os.path.join(base_dir, "qml")

        setup_quick_widget(self._road_quick_widget, self._view_models.road_list_model,
                           os.path.join(qml_folder, "RoadListView.qml"))
        setup_quick_widget(self._car_quick_widget, self._view_models.car_list_model,
                           os.path.join(qml_folder, "CarListView.qml"))
        setup_quick_widget(self._query_quick_widget, self._view_models.query_list_model,
                           os.path.join(qml_folder, "RoadListView.qml"))

    def open_edit_dialog(self, edit_dialog) -> None:
        dialog = edit_dialog(None, parent=self._window, application_controller=self._application_controller)
        dialog.exec()
