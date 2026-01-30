from PySide6.QtCore import QObject, QUrl, Qt

from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.controllers.view_event_contract import ViewEventHandler
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.view.ui.lists.models.RoadModel import RoadModel
from pse.umlsl_editor.src.view.ui.lists.edit_car_dialog import EditCarDialog
from pse.umlsl_editor.src.view.ui.lists.edit_query_dialog import EditQueryDialog
from pse.umlsl_editor.src.view.ui.lists.edit_road_dialog import EditRoadDialog
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class SidebarController(QObject):
    def __init__(self, main_window: Ui_MainWindow, data_controller: DataController) -> None:
        super().__init__(main_window)
        self._models = data_controller.get_view_models()
        self.window = main_window

        self.road_quick_widget = self.window.q_roads
        self.car_quick_widget = self.window.q_cars
        self.query_quick_widget = self.window.q_queries

        self.add_road_button = self.window.b_add_road
        self.add_car_button = self.window.b_add_car
        self.add_query_button = self.window.b_add_query

        self.setup_ui()

    def setup_ui(self) -> None:
        """Connect button click signals."""
        self.add_road_button.clicked.connect(lambda: self.open_edit_dialog(EditRoadDialog))
        self.add_car_button.clicked.connect(lambda: self.open_edit_dialog(EditCarDialog))
        self.add_query_button.clicked.connect(lambda: self.open_edit_dialog(EditQueryDialog))

        def setup_quick_widget(quick_widget, model, qml_file_path: str) -> None:
            """Set up a QML Quick Widget with the given model and QML file."""
            quick_widget.setClearColor(Qt.transparent)
            quick_widget.setAttribute(Qt.WA_TranslucentBackground)
            quick_widget.setAttribute(Qt.WA_AlwaysStackOnTop)
            quick_widget.setResizeMode(quick_widget.ResizeMode.SizeRootObjectToView)

            quick_widget.rootContext().setContextProperty("data_model", model)
            quick_widget.setSource(QUrl.fromLocalFile(qml_file_path))

        setup_quick_widget(self.road_quick_widget, self._models.road_list_model, "../ui/lists/qml/RoadListView.qml")
        setup_quick_widget(self.car_quick_widget, self._models.car_list_model, "../ui/lists/qml/CarListView.qml")
        setup_quick_widget(self.query_quick_widget, self._models.query_list_model, "../ui/lists/qml/RoadListView.qml")



    def open_edit_dialog(self, edit_dialog ) -> None:
        dialog = edit_dialog(self.window)
        dialog.exec()

