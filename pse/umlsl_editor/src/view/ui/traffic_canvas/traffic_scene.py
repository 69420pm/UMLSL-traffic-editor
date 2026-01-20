"""
Traffic scene for the UMLSL Traffic Editor.

Manages the QGraphicsScene containing all traffic entities (roads, cars, crossings).
"""
from typing import Any, Dict

from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide6.QtCore import QRectF

from pse.umlsl_editor.src.view.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.view_constants import DIMENSION



class TrafficScene(QGraphicsScene):
    """
    Graphics scene containing all traffic entities.

    Manages the visual representation of roads, cars, and crossings.
    Provides a registry for tracking items and a cache for road data.
    """

    def __init__(self, parent=None):
        """Initialize the traffic scene with configured bounds."""
        super().__init__(parent)

        # Set up scene bounds
        size = DIMENSION.SCENE_SIZE
        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

        # Registry to track graphics items by entity ID
        self._items_registry: Dict[str, QGraphicsItem] = {}

    def add_entity(self, data_object: Any) -> None:
        pass

    def remove_entity(self, data_object: Any) -> None:
        pass

    def update_entity(self, data_object: Any) -> None:
        road_item = RoadItem(data_object)
        self.addItem(road_item)