from typing import Any
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt

from pse.umlsl_editor.src.view.canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.canvas.traffic_view import TrafficCanvasView
from pse.umlsl_editor.src.view.sidebar.sidebar_widget import SidebarWidget
from pse.umlsl_editor.src.view.traffic_view import TrafficView
from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road
from pse.umlsl_editor.src.core.dataclasses.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.core.dataclasses.umlsl_query import UMLSLQuery


class MainWindow(QMainWindow, TrafficView):
    """
    The main application window with sidebar and canvas.
    """
    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        # Set window properties
        self.setWindowTitle("UMLSL Traffic Editor")
        self.resize(1200, 800)

        # Create the scene and view
        self.scene = TrafficScene()
        self.canvas_view = TrafficCanvasView(self.scene)

        # Create the sidebar
        self.sidebar = SidebarWidget()

        # Create a splitter to allow resizing between sidebar and canvas
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.canvas_view)

        # Set initial sizes (sidebar 300px, canvas takes the rest)
        splitter.setSizes([300, 900])

        # Set the splitter as central widget
        self.setCentralWidget(splitter)

    def get_scene(self) -> TrafficScene:
        """
        Returns the TrafficScene instance used by the main window.
        """
        return self.scene

    def get_sidebar(self) -> SidebarWidget:
        """
        Returns the SidebarWidget instance.
        """
        return self.sidebar

    # Car view methods
    def add_car_view(self, car_data: Car) -> None:
        """Add car to both canvas and sidebar."""
        self.scene.add_car_item(car_data)
        self.sidebar.add_car(car_data)

    def remove_car_view(self, car_data: Car) -> None:
        """Remove car from both canvas and sidebar."""
        self.scene.remove_car_item(car_data)
        self.sidebar.remove_car(car_data)

    def update_car_view(self, car_data: Car) -> None:
        """Update car in both canvas and sidebar."""
        self.scene.update_car_item(car_data)
        self.sidebar.update_car(car_data)

    # Road view methods
    def add_road_view(self, road_data: Road) -> None:
        """Add road to both canvas and sidebar."""
        self.scene.add_road_item(road_data)
        self.sidebar.add_road(road_data)

    def remove_road_view(self, road_data: Road) -> None:
        """Remove road from both canvas and sidebar."""
        self.scene.remove_road_item(road_data)
        self.sidebar.remove_road(road_data)

    def update_road_view(self, road_data: Road) -> None:
        """Update road in both canvas and sidebar."""
        self.scene.update_road_item(road_data)
        self.sidebar.update_road(road_data)

    # Crossing segment view methods
    def add_crossing_segment_view(self, crossing_data: CrossingSegment) -> None:
        """Add crossing segment to canvas."""
        self.scene.add_crossing_segment_item(crossing_data)

    def remove_crossing_segment_view(self, crossing_data: CrossingSegment) -> None:
        """Remove crossing segment from canvas."""
        self.scene.remove_crossing_segment_item(crossing_data)

    def update_crossing_segment_view(self, crossing_data: CrossingSegment) -> None:
        """Update crossing segment in canvas."""
        self.scene.update_crossing_segment_item(crossing_data)

    # UMLSL Query view methods
    def add_query_view(self, query_data: UMLSLQuery) -> None:
        """Add UMLSL query to sidebar."""
        self.sidebar.add_query(query_data)

    def remove_query_view(self, query_data: UMLSLQuery) -> None:
        """Remove UMLSL query from sidebar."""
        self.sidebar.remove_query(query_data)

    def update_query_view(self, query_data: UMLSLQuery) -> None:
        """Update UMLSL query in sidebar."""
        self.sidebar.update_query(query_data)

