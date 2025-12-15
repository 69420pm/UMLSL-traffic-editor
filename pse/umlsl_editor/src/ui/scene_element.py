from typing import List, Any

from pse.umlsl_editor.src.core.car import Car
from pse.umlsl_editor.src.core.road import Road
from pse.umlsl_editor.src.ui.coordinate_system import CoordinateSystem
from pse.umlsl_editor.src.ui.scene import SceneManager


class RoadGraphicsItem:
    """Visual wrapper (e.g., QGraphicsItem)."""

    def __init__(self, road: Road):
        self.road = road

    def paint(self, painter): pass


class CarGraphicsItem:
    """Visual wrapper."""

    def __init__(self, car: Car):
        self.car = car

    def paint(self, painter): pass


class TrafficVisualEditor:
    """The Canvas Widget (View)."""

    def __init__(self):
        self.scene_manager = SceneManager(self)
        self.coord_sys = CoordinateSystem()

    def zoom(self, factor: float): pass

    def pan(self, dx: float, dy: float): pass


class LaTeXPreviewWidget:
    """Uses Matplotlib to render LaTeX to an image buffer."""

    def render(self, latex: str):
        pass


class EntityListWidget:
    """Generic list for sidebar items."""

    def set_items(self, items: List[Any]): pass

    def highlight_item(self, id_: str): pass


class ConfigurationPanel:
    """Left Sidebar."""

    def __init__(self):
        self.road_list = EntityListWidget()
        self.car_list = EntityListWidget()
        self.query_list = EntityListWidget()
