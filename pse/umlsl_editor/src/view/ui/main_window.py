from PySide6.QtWidgets import QMainWindow

from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.view.ui.global_controlls import GlobalControls
from pse.umlsl_editor.src.view.ui.lists.sidebar_controller import SidebarController
from pse.umlsl_editor.src.view.ui.traffic_canvas.canvas_buttons import CanvasButtons
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_view import TrafficView
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, data_controller: DataController) -> None:
        super().__init__()

        self.setupUi(self)

        self.traffic_scene = TrafficScene(data_controller=data_controller)
        self.trafficView = TrafficView(scene=self.traffic_scene)

        layout = self.graphicsView.parentWidget().layout()
        layout.replaceWidget(self.graphicsView, self.trafficView)
        self.graphicsView.deleteLater()


        self.canvas_buttons = CanvasButtons(self)

        self.sidebar_controller = SidebarController(self)

        self.global_controls = GlobalControls(self)

        self.show()
