"""
Main window module for the UMLSL Traffic Editor.

This module contains the MainWindow class, which serves as the primary
application window and coordinates all UI components.
"""

from PySide6.QtWidgets import QMainWindow

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.global_controlls import GlobalControls
from pse.umlsl_editor.src.view.ui.lists.sidebar_controller import SidebarController
from pse.umlsl_editor.src.view.ui.traffic_canvas.canvas_buttons import CanvasButtons
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_view import TrafficView
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Primary application window for the UMLSL Traffic Editor.

    This class integrates all major UI components including the traffic canvas,
    sidebar controls, and global application controls. It inherits from both
    QMainWindow for Qt functionality and Ui_MainWindow for the compiled UI layout.

    Attributes:
        traffic_scene: The graphics scene containing all traffic entities.
        trafficView: The graphics view for rendering and interacting with the scene.
        canvas_buttons: Controller for zoom and overlay buttons on the canvas.
        sidebar_controller: Controller for the sidebar entity lists.
        global_controls: Controller for menu actions (save, open, settings).
    """

    def __init__(self, application_controller: ApplicationController) -> None:
        """
        Initialize the main window with all UI components.

        Args:
            application_controller: The central controller managing application
                state and coordinating between model, view, and commands.
        """
        super().__init__()
        self.setupUi(self)

        self._setup_traffic_canvas(application_controller)
        self._setup_controllers(application_controller)

    def _setup_traffic_canvas(self, application_controller: ApplicationController) -> None:
        """
        Initialize and configure the traffic canvas components.

        Replaces the placeholder graphics view from the UI file with the
        custom TrafficView and TrafficScene.

        Args:
            application_controller: The application controller for scene initialization.
        """
        self.traffic_scene = TrafficScene(application_controller)
        self.trafficView = TrafficView(scene=self.traffic_scene)

        layout = self.graphicsView.parentWidget().layout()
        layout.replaceWidget(self.graphicsView, self.trafficView)
        self.graphicsView.deleteLater()

    def _setup_controllers(self, application_controller: ApplicationController) -> None:
        """
        Initialize UI controllers for various window components.

        Args:
            application_controller: The application controller passed to child controllers.
        """
        self.canvas_buttons = CanvasButtons(self)
        self.sidebar_controller = SidebarController(self, application_controller)
        self.global_controls = GlobalControls(self)
