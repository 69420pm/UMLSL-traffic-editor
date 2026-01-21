from PySide6.QtWidgets import QMainWindow

from pse.umlsl_editor.src.view.testing.sample_scene_generator import create_sample_scene
from pse.umlsl_editor.src.view.ui.global_controlls import GlobalControls
from pse.umlsl_editor.src.view.ui.lists.sidebar_controller import SidebarController
from pse.umlsl_editor.src.view.ui.traffic_canvas.canvas_buttons import CanvasButtons
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        self.setupUi(self)

        self.traffic_scene = TrafficScene()
        self.trafficView.setScene(self.traffic_scene)

        self.canvas_buttons = CanvasButtons(self)
        self.canvas_buttons.setup_ui()

        self.sidebar_controller = SidebarController(self)
        self.sidebar_controller.setup_ui()

        self.global_controls = GlobalControls(self)
        self.global_controls.setup_ui()

        self._load_sample_scene()
        self.show()

    def _load_sample_scene(self) -> None:
        """Load a sample scene for testing purposes."""
        entities = create_sample_scene()
        for entity in entities:
            self.traffic_scene.update_entity(entity)
