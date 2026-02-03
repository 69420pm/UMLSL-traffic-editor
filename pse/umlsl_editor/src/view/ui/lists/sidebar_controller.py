"""
Sidebar controller for the UMLSL Traffic Editor.

Manages the sidebar UI including entity lists (roads, cars, queries) and
their associated QML views and add buttons.
"""

import os

from PySide6.QtCore import QObject, Qt, QUrl

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.lists.edit_car_dialog import EditCarDialog
from pse.umlsl_editor.src.view.ui.lists.edit_query_dialog import EditQueryDialog
from pse.umlsl_editor.src.view.ui.lists.edit_road_dialog import EditRoadDialog
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class SidebarController(QObject):
    """
    Controller for the sidebar panel containing entity lists.

    Manages the QML-based list views for roads, cars, and queries, and handles
    the add buttons for creating new entities. Each list is backed by a model
    from the view event handler.

    Attributes:
        _view_models: Collection of view models for entity lists.
        _application_controller: Reference to the main application controller.
        _window: Reference to the main application window.
    """

    def __init__(
            self,
            main_window: Ui_MainWindow,
            application_controller: ApplicationController,
    ) -> None:
        """
        Initialize the sidebar controller.

        Args:
            main_window: The main application window containing sidebar widgets.
            application_controller: The central controller for coordinating
                model-view interactions.
        """
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

        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configure button connections and initialize QML list views."""
        self._connect_add_buttons()
        self._setup_quick_widgets()

    def _connect_add_buttons(self) -> None:
        """Connect add buttons to their respective dialog handlers."""
        self._add_road_button.clicked.connect(
            lambda: self._open_edit_dialog(EditRoadDialog)
        )
        self._add_car_button.clicked.connect(
            lambda: self._open_edit_dialog(EditCarDialog)
        )
        self._add_query_button.clicked.connect(
            lambda: self._open_edit_dialog(EditQueryDialog)
        )

    def _setup_quick_widgets(self) -> None:
        """Initialize all QML Quick Widgets with their models and QML files."""
        qml_folder = self._get_qml_folder_path()

        self._configure_quick_widget(
            self._road_quick_widget,
            self._view_models.road_list_model,
            os.path.join(qml_folder, "RoadListView.qml"),
        )
        self._configure_quick_widget(
            self._car_quick_widget,
            self._view_models.car_list_model,
            os.path.join(qml_folder, "CarListView.qml"),
        )
        self._configure_quick_widget(
            self._query_quick_widget,
            self._view_models.query_list_model,
            os.path.join(qml_folder, "QueryListView.qml"),
        )

    def _get_qml_folder_path(self) -> str:
        """
        Get the absolute path to the QML folder.

        Returns:
            Absolute path to the qml subfolder relative to this module.
        """
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, "qml")

    def _configure_quick_widget(
            self,
            quick_widget,
            model,
            qml_file_path: str,
    ) -> None:
        """
        Configure a QML Quick Widget with the specified model and QML file.

        Sets up transparency, resize behavior, and binds the data model
        to the QML context.

        Args:
            quick_widget: The QQuickWidget to configure.
            model: The data model to expose to QML.
            qml_file_path: Path to the QML file defining the view.
        """
        quick_widget.setClearColor(Qt.transparent)
        quick_widget.setAttribute(Qt.WA_TranslucentBackground)
        quick_widget.setAttribute(Qt.WA_AlwaysStackOnTop)
        quick_widget.setResizeMode(quick_widget.ResizeMode.SizeRootObjectToView)

        quick_widget.rootContext().setContextProperty("data_model", model)
        quick_widget.setSource(QUrl.fromLocalFile(qml_file_path))

    def _open_edit_dialog(self, dialog_class) -> None:
        """
        Open an edit dialog for creating a new entity.

        Args:
            dialog_class: The dialog class to instantiate (e.g., EditRoadDialog).
        """
        dialog = dialog_class(
            None,
            parent=self._window,
            application_controller=self._application_controller,
        )
        dialog.exec()
