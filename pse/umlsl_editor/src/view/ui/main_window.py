from pse.umlsl_editor.src.view.traffic_canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.ui.global_controls import GlobalControls
from pse.umlsl_editor.src.view.ui.lists.car_list import CarListController
from pse.umlsl_editor.src.view.ui.lists.query_list import QueryListController
from pse.umlsl_editor.src.view.ui.lists.road_list import RoadListController
from pse.umlsl_editor.src.view.ui_utils import load_ui


class MainWindow:
    def __init__(self):
        self.ui = load_ui("ui/main.ui")

        self.car_controller = CarListController(self.ui)
        self.road_controller = RoadListController(self.ui)
        self.query_controller = QueryListController(self.ui)
        self.global_controls = GlobalControls(self.ui)
        self.traffic_scene = TrafficScene(self.ui)
        self.canvas_buttons = CanvasButtons(self.ui)

    def setup_ui(self):
        pass