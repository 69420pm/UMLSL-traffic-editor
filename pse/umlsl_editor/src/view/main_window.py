from typing import Any
from PySide6.QtWidgets import QMainWindow, QGraphicsView
from pse.umlsl_editor.src.view.canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.traffic_view import TrafficView

class MainWindow(QMainWindow, TrafficView):
    """
    The main application window.
    """
    def __init__(self):
        super().__init__()
        self.scene = TrafficScene()
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

    def get_scene(self) -> TrafficScene:
        """
        Returns the TrafficScene instance used by the main window.
        """
        return self.scene

    def add_car_view(self, car_data: Any) -> None:
        self.scene.add_car_item(car_data)

    def remove_car_view(self, car_data: Any) -> None:
        self.scene.remove_car_item(car_data)

    def update_car_view(self, car_data: Any) -> None:
        self.scene.update_car_item(car_data)

    def add_road_view(self, road_data: Any) -> None:
        self.scene.add_road_item(road_data)

    def remove_road_view(self, road_data: Any) -> None:
        self.scene.remove_road_item(road_data)

    def update_road_view(self, road_data: Any) -> None:
        self.scene.update_road_item(road_data)

