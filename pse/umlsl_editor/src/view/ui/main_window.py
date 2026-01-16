from PySide6.QtUiTools import QUiLoader

from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_view import TrafficView
from pse.umlsl_editor.src.view.ui_utils import load_ui


class MainWindow:
    def __init__(self):
        self.loader = QUiLoader()
        self.loader.registerCustomWidget(TrafficView)

        self.ui = load_ui("../widgets/main.ui")

        #self.car_controller = CarListController(self.ui)
        #self.road_controller = RoadListController(self.ui)
        #self.query_controller = QueryListController(self.ui)
        #self.global_controls = GlobalControls(self.ui)
        #self.canvas_buttons = CanvasButtons(self.ui)

        self.traffic_scene = TrafficScene()
        self.traffic_view = self.ui.findChild(TrafficView, "trafficView")

        if self.traffic_view:
            self.traffic_view.setScene(self.traffic_scene)
        else:
            print("Could not find 'trafficView' in the .ui file!")


        self.ui.show()