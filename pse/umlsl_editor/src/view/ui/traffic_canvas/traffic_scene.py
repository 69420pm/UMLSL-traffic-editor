from typing import Any, Optional

from PySide6.QtWidgets import QGraphicsScene, QGraphicsRectItem, QGraphicsPathItem, QGraphicsItem
from PySide6.QtCore import QRectF

from pse.umlsl_editor.src.view.view_constants import DIMENSION, COLORS, Z_LAYERS

# --- Import Entities ---
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment

# --- Import View Models ---
from pse.umlsl_editor.src.view.view_models.car_view_model import CarViewModel
from pse.umlsl_editor.src.view.view_models.crossing_view_model import CrossingViewModel
from pse.umlsl_editor.src.view.view_models.road_view_model import RoadViewModel


def _get_unique_id(data: Any) -> Optional[str]:
    """Generates a stable string ID for any entity."""
    if isinstance(data, Car):
        return f"car_{data.name}"
    elif isinstance(data, Road):
        return f"road_{data.name}"
    elif isinstance(data, CrossingSegment):
        # Create a composite ID for the crossing based on the lanes it connects
        h_lane = data.lane_horizontal
        v_lane = data.lane_vertical
        return f"cross_{h_lane.road_name}_{h_lane.lane_index}_x_{v_lane.road_name}_{v_lane.lane_index}"
    return None


class TrafficScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(TrafficScene, self).__init__(parent)

        # 1. Setup Scene Bounds (as discussed)
        size = DIMENSION.SCENE_SIZE
        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

        # 2. Item Registry
        # Maps unique ID -> (QGraphicsItem, ViewModel)
        self._items: dict[str, tuple[QGraphicsItem, Any]] = {}

        # 3. Road Data Cache (Acts as 'RoadAccessor' for ViewModels)
        self._road_cache: dict[str, Road] = {}

    # --- RoadAccessor Protocol Implementation ---
    def get_road(self, road_name: str) -> Optional[Road]:
        """Allows ViewModels (like CrossingViewModel) to ask for road geometry."""
        return self._road_cache.get(road_name)

    # --- Main Draw / Update Logic ---
    def update_entity(self, data_object: Any):
        """
        The single entry point for redrawing.
        Detects the type of data (Car, Road, Crossing) and updates the UI accordingly.
        """
        uid = _get_unique_id(data_object)
        if not uid:
            return

        # 1. Update Cache if it's a road
        if isinstance(data_object, Road):
            self._road_cache[uid] = data_object

        # 2. Create if not exists
        if uid not in self._items:
            self._create_item(uid, data_object)

        # 3. Update existing item
        self._update_item_visuals(uid, data_object)

    def remove_entity(self, data_object: Any):
        """Removes the entity from the scene."""
        uid = _get_unique_id(data_object)
        if uid in self._items:
            item, _ = self._items[uid]
            self.removeItem(item)
            del self._items[uid]

            # Clean cache if needed
            if isinstance(data_object, Road) and uid in self._road_cache:
                del self._road_cache[uid]

    # --- Internal Helpers ---

    def _create_item(self, uid: str, data: Any):
        """Factory method: Instantiates the correct ViewModel and QGraphicsItem."""
        item = None
        vm = None

        if isinstance(data, Road):
            vm = RoadViewModel(data)
            item = QGraphicsRectItem()  # Roads are rectangles
            item.setZValue(Z_LAYERS.ROAD)

        elif isinstance(data, Car):
            # Pass 'self' because TrafficScene acts as the RoadAccessor
            vm = CarViewModel(data, road_accessor=self)
            item = QGraphicsRectItem()
            item.setZValue(Z_LAYERS.CAR)

        elif isinstance(data, CrossingSegment):
            vm = CrossingViewModel(data, road_accessor=self)
            item = QGraphicsPathItem()  # Crossings are complex shapes (Paths)
            item.setZValue(Z_LAYERS.CROSSING)

        if item and vm:
            self.addItem(item)
            self._items[uid] = (item, vm)

    def _update_item_visuals(self, uid: str, data: Any):
        """Pushes data to ViewModel -> Pulls geometry to GraphicsItem."""
        item, vm = self._items[uid]

        # 1. Logic: Update the ViewModel (Recalculate Math)
        vm.update(data)

        # 2. Visuals: Apply calculated geometry to Qt Item
        if isinstance(item, QGraphicsRectItem):
            item.setRect(vm.bounding_rect)
        elif isinstance(item, QGraphicsPathItem):
            item.setPath(vm.shape)

        # 3. Apply Styling
        item.setBrush(vm.color)
        # item.setPen(...) if you want borders