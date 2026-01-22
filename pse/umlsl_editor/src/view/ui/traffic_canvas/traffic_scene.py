"""
Traffic scene for the UMLSL Traffic Editor.

Manages the QGraphicsScene containing all traffic entities (roads, cars, crossings).
"""
from typing import Any, Dict

from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem
from PySide6.QtCore import QRectF

from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.crossing_item import CrossingItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
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

    def remove_entity(self, data_object: Any) -> None:
        pass

    def add_entity(self, data_object: Any) -> None:
        # Create the new road item
        new_road_item = RoadItem(data_object)
        self.addItem(new_road_item)
        self._items_registry[data_object.uid] = new_road_item

        print("Added road:", new_road_item)

        # NEW: Check for intersections with existing roads
        self._check_and_create_crossings(new_road_item)

    def _check_and_create_crossings(self, new_road_item: RoadItem):
        """Finds perpendicular roads and creates crossings."""
        new_orientation = new_road_item.data(0).orientation

        for existing_road in self._items_registry.values():
            print(existing_road)
            # Only create crossing if orientations differ (one H, one V)
            if existing_road.data(0).orientation != new_orientation:
                self._create_crossing(new_road_item, existing_road)

    def _create_crossing(self, road_a: RoadItem, road_b: RoadItem):
        print("Creating crossing between roads")
        """Instantiates a crossing and links it to both roads."""
        crossing = CrossingItem(road_a, road_b)
        self.addItem(crossing)

        # Register the crossing as a listener to both roads
        # This ensures it moves if EITHER road is dragged
        road_a.add_position_listener(crossing)
        road_b.add_position_listener(crossing)