"""
Traffic scene for the UMLSL Traffic Editor.

Manages the QGraphicsScene containing all traffic entities (roads, cars, crossings).
"""
from typing import Any, Optional

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import QRectF

from pse.umlsl_editor.src.view.view_constants import DIMENSION, Z_LAYERS
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.view.view_models.car_view_model import CarViewModel
from pse.umlsl_editor.src.view.view_models.road_graphics_item import RoadGraphicsItem
from pse.umlsl_editor.src.view.view_models.road_view_model import RoadViewModel


def _get_unique_id(data: Any) -> Optional[str]:
    """
    Generate a stable string ID for any traffic entity.

    Args:
        data: The entity to generate an ID for.

    Returns:
        A unique string identifier, or None if the entity type is unknown.
    """
    if isinstance(data, Car):
        return f"car_{data.name}"
    elif isinstance(data, Road):
        return f"road_{data.name}"
    elif isinstance(data, CrossingSegment):
        h_lane = data.lane_horizontal
        v_lane = data.lane_vertical
        return f"cross_{h_lane.road_name}_{h_lane.lane_index}_x_{v_lane.road_name}_{v_lane.lane_index}"
    return None


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

        # Item registry: maps unique ID -> (QGraphicsItem, ViewModel)
        self._items: dict[str, tuple[QGraphicsItem, Any]] = {}

        # Road data cache (acts as RoadAccessor for ViewModels)
        self._road_cache: dict[str, Road] = {}

    @property
    def roads(self) -> list[Road]:
        """Return all cached roads for lane label rendering."""
        return list(self._road_cache.values())

    # --- Public API ---

    def update_entity(self, data_object: Any) -> None:
        """
        Update or create the visual representation of an entity.

        Args:
            data_object: The entity (Car, Road, or CrossingSegment) to update.
        """
        uid = _get_unique_id(data_object)
        if not uid:
            return

        # Update cache for roads
        if isinstance(data_object, Road):
            self._road_cache[uid] = data_object

        # Create if not exists
        if uid not in self._items:
            self._create_item(uid, data_object)

        # Update existing item
        self._update_item_visuals(uid, data_object)

    def remove_entity(self, data_object: Any) -> None:
        """
        Remove an entity from the scene.

        Args:
            data_object: The entity to remove.
        """
        uid = _get_unique_id(data_object)
        if uid in self._items:
            item, _ = self._items[uid]
            self.removeItem(item)
            del self._items[uid]

            if isinstance(data_object, Road) and uid in self._road_cache:
                del self._road_cache[uid]

    # --- Private Helpers ---

    def _create_item(self, uid: str, data: Any) -> None:
        """Create the appropriate graphics item for the given entity."""
        item = None
        vm = None

        if isinstance(data, Road):
            vm = RoadViewModel(data)
            item = RoadGraphicsItem(vm)
            item.setZValue(Z_LAYERS.ROAD)

        elif isinstance(data, Car):
            vm = CarViewModel(data, road_accessor=self)
            item = QGraphicsRectItem(vm.bounding_rect)

        if item and vm:
            self.addItem(item)
            self._items[uid] = (item, vm)

    def _update_item_visuals(self, uid: str, data: Any) -> None:
        """Update the visuals of an existing item."""
        item, vm = self._items[uid]

        # Update the view model
        vm.update(data)

        # Update the graphics item
        if isinstance(item, RoadGraphicsItem):
            item.update_visuals(vm)
        elif isinstance(item, QGraphicsRectItem):
            item.setRect(vm.bounding_rect)
            item.setBrush(vm.color)
            if hasattr(vm, 'pen'):
                item.setPen(vm.pen)

