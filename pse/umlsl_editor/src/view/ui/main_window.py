"""
Main window for the UMLSL Traffic Editor.

Contains the primary application window setup and initialization.
"""
from PySide6.QtUiTools import QUiLoader

from pse.umlsl_editor.src.view.testing.sample_scene_generator import create_sample_scene
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_view import TrafficView
from pse.umlsl_editor.src.view.ui_utils import load_ui
from pse.umlsl_editor.src.view.view_constants import UI_PATHS


class MainWindow:
    """
    Main application window that coordinates all UI components.

    Manages the traffic scene, view, and auxiliary controllers for
    cars, roads, queries, and global controls.
    """

    def __init__(self):
        """Initialize the main window and all its components."""
        self.loader = QUiLoader()
        self.loader.registerCustomWidget(TrafficView)

        self.ui = load_ui(UI_PATHS.MAIN_WINDOW)

        # Initialize traffic scene and view
        self.traffic_scene = TrafficScene()
        self.traffic_view = self.ui.findChild(TrafficView, "trafficView")
        self.traffic_view.setScene(self.traffic_scene)

        # Load sample scene for testing
        self._load_sample_scene()

        self.ui.show()

    def _load_sample_scene(self) -> None:
        """Load a sample scene for testing purposes."""
        entities = create_sample_scene()
        for entity in entities:
            self.traffic_scene.update_entity(entity)
