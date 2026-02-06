"""
Traffic scene for the UMLSL Traffic Editor.

This module provides the QGraphicsScene that manages all visual traffic entities
including roads, cars, crossings, and debug segments. It observes the list models
and automatically creates, updates, and removes graphics items in response to
model changes.
"""

import logging
from typing import Dict

from PySide6.QtCore import QModelIndex, QRectF
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.car_item import CarItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.crossing_item import (
    CrossingItem,
)
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.debug_segment_item import (
    DebugSegmentItem,
)
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.view_constants import DIMENSION

logger = logging.getLogger(__name__)

SHOW_DEBUG_SEGMENTS = True


class TrafficScene(QGraphicsScene):
    """
    Graphics scene containing all visual traffic entities.

    Manages the lifecycle of graphics items by observing changes in the underlying
    list models (CarListModel, RoadListModel).
    """

    def __init__(
            self,
            application_controller: ApplicationController,
            parent=None,
    ) -> None:
        super().__init__(parent)

        size = DIMENSION.SCENE_SIZE
        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

        self._app_controller = application_controller

        # Registries
        self._item_registry: Dict[str, QGraphicsItem] = {}
        self._debug_registry: Dict[str, DebugSegmentItem] = {}

        # Models
        view_models = application_controller.view_event_handler.view_models
        self._car_model = view_models.car_list_model
        self._road_model = view_models.road_list_model

        self._connect_model_signals()

    def _connect_model_signals(self) -> None:
        """Connect to model signals to observe entity changes."""
        # Cars
        self._car_model.rowsInserted.connect(self._on_cars_added)
        self._car_model.rowsAboutToBeRemoved.connect(self._on_cars_removed)
        self._car_model.dataChanged.connect(self._on_car_data_changed)
        self._car_model.modelReset.connect(self._on_models_reset)

        # Roads
        self._road_model.rowsInserted.connect(self._on_roads_added)
        self._road_model.rowsAboutToBeRemoved.connect(self._on_roads_removed)
        self._road_model.dataChanged.connect(self._on_road_data_changed)
        self._road_model.modelReset.connect(self._on_models_reset)

    def _on_models_reset(self) -> None:
        """Clear all rendered items when list models reset."""
        for item in list(self._item_registry.values()):
            if isinstance(item, CarItem):
                item.cleanup()
            elif isinstance(item, RoadItem):
                for listener in list(item.position_listeners):
                    if isinstance(listener, CrossingItem):
                        self._remove_crossing(listener)
        self.clear()
        self._item_registry.clear()
        self._debug_registry.clear()

    # -------------------------------------------------------------------------
    # Car Model Handlers
    # -------------------------------------------------------------------------

    def _on_cars_added(self, parent: QModelIndex, first: int, last: int) -> None:
        """Creates CarItem for new cars. CarItem auto-registers listeners."""
        for row in range(first, last + 1):
            car: Car = self._car_model.get_entity_at(row)

            # Find the road item this car belongs to
            road_item = self._item_registry.get(car.lane.road_uid)
            if not isinstance(road_item, RoadItem):
                logger.warning(f"Skipping car {car.uid}: Assigned road {car.lane.road_uid} not found.")
                continue

            graphics_item = CarItem(car, road_item, self._app_controller)

            self.addItem(graphics_item)
            self._item_registry[car.uid] = graphics_item

    def _on_car_data_changed(
            self,
            top_left: QModelIndex,
            bottom_right: QModelIndex,
            roles,
    ) -> None:
        """Updates CarItem. Handles visual updates and road re-assignment internally."""
        for row in range(top_left.row(), bottom_right.row() + 1):
            updated_car: Car = self._car_model.get_entity_at(row)
            car_item = self._item_registry.get(updated_car.uid)

            if not isinstance(car_item, CarItem):
                continue

            # Check if road changed
            target_road_uid = updated_car.lane.road_uid
            new_road_item = self._item_registry.get(target_road_uid)

            if isinstance(new_road_item, RoadItem):
                # CarItem handles listener switching if new_road_item differs from current
                car_item.update_data(updated_car, new_road_item)
            else:
                logger.error(f"Cannot update car {updated_car.uid}: Road {target_road_uid} missing.")

    def _on_cars_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        """Removes CarItem and cleans up listeners."""
        for row in range(first, last + 1):
            car: Car = self._car_model.get_entity_at(row)
            car_item = self._item_registry.pop(car.uid, None)

            if isinstance(car_item, CarItem):
                car_item.cleanup()  # Important: Detaches from RoadItem
                self.removeItem(car_item)

    # -------------------------------------------------------------------------
    # Road Model Handlers
    # -------------------------------------------------------------------------

    def _on_roads_added(self, parent: QModelIndex, first: int, last: int) -> None:
        """Creates RoadItem, generates crossings, and claims orphaned cars."""
        for row in range(first, last + 1):
            road: Road = self._road_model.get_entity_at(row)
            graphics_item = RoadItem(road, self._app_controller)

            self.addItem(graphics_item)
            self._item_registry[road.uid] = graphics_item

            self._check_and_create_crossings(graphics_item)
            self._reassign_orphaned_cars(road, graphics_item)

            if SHOW_DEBUG_SEGMENTS: self._refresh_debug_segments()

    def _reassign_orphaned_cars(self, road: Road, road_item: RoadItem) -> None:
        """
        Updates existing cars that belong to this new road.
        Useful if cars were loaded before their roads.
        """
        for item in self._item_registry.values():
            if isinstance(item, CarItem):
                car_entity = item.data(0)
                if car_entity.lane.road_uid == road.uid:
                    # CarItem will automatically attach listener to the new road_item
                    item.update_data(car_entity, road_item)

    def _on_road_data_changed(
            self,
            top_left: QModelIndex,
            bottom_right: QModelIndex,
            roles,
    ) -> None:
        """Updates RoadItem visuals."""
        for row in range(top_left.row(), bottom_right.row() + 1):
            road: Road = self._road_model.get_entity_at(row)
            road_item = self._item_registry.get(road.uid)

            if isinstance(road_item, RoadItem):
                road_item.update_data(road)

        if SHOW_DEBUG_SEGMENTS: self._refresh_debug_segments()

    def _on_roads_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        """Removes RoadItem and associated crossings."""
        for row in range(first, last + 1):
            road: Road = self._road_model.get_entity_at(row)
            road_item = self._item_registry.pop(road.uid, None)

            if not isinstance(road_item, RoadItem):
                continue

            # Remove connected crossings
            # We iterate a copy because removal modifies the list
            # FIX: Access _position_listeners (protected member)
            for listener in list(road_item.position_listeners):
                if isinstance(listener, CrossingItem):
                    self._remove_crossing(listener)

            self.removeItem(road_item)

        if SHOW_DEBUG_SEGMENTS: self._refresh_debug_segments()

    # -------------------------------------------------------------------------
    # Crossing Management
    # -------------------------------------------------------------------------

    def _check_and_create_crossings(self, new_road_item: RoadItem) -> None:
        """Detects intersections with existing roads and creates CrossingItems."""
        new_orientation = new_road_item.data(0).orientation

        for existing_item in self._item_registry.values():
            if not isinstance(existing_item, RoadItem):
                continue

            # Only cross perpendicular roads
            if existing_item.data(0).orientation != new_orientation:
                self._create_crossing(new_road_item, existing_item)

    def _create_crossing(self, road_a: RoadItem, road_b: RoadItem) -> None:
        """Creates a crossing and registers it as a listener on both roads."""
        crossing = CrossingItem(road_a, road_b)
        self.addItem(crossing)

    def _remove_crossing(self, crossing: CrossingItem) -> None:
        """Removes a crossing."""
        crossing.cleanup()
        self.removeItem(crossing)

    # -------------------------------------------------------------------------
    # Debug Segments
    # -------------------------------------------------------------------------

    def _refresh_debug_segments(self) -> None:
        """Recreates debug visualizations from snapshot data."""
        for item in self._debug_registry.values():
            self.removeItem(item)
        self._debug_registry.clear()

        snapshot_reader = self._app_controller.get_traffic_snapshot_reader()
        if not snapshot_reader:
            return

        segments = snapshot_reader.debug_get_segments()
        for segment in segments.values():
            item = DebugSegmentItem(segment, self._app_controller)
            self._debug_registry[segment.uid] = item
            self.addItem(item)
