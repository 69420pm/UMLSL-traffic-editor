"""
Traffic scene for the UMLSL Traffic Editor.

This module provides the QGraphicsScene that manages all visual traffic entities
including roads, cars, crossings, and debug segments. It observes the list models
and automatically creates, updates, and removes graphics items in response to
model changes.
"""

from PySide6.QtCore import QModelIndex, QRectF
from PySide6.QtWidgets import QGraphicsScene

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.car_item import CarItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.crossing_item import (
    CrossingItem,
)
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.debug_segment_item import (
    DebugSegmentItem,
)
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.view_constants import DIMENSION


class TrafficScene(QGraphicsScene):
    """
    Graphics scene containing all visual traffic entities.

    This class manages the lifecycle of graphics items (roads, cars, crossings)
    by observing changes in the underlying list models. When entities are added,
    updated, or removed from the models, the scene automatically reflects those
    changes by creating, updating, or removing the corresponding graphics items.

    Attributes:
        _application_controller: Reference to the central application controller.
        _item_registry: Dictionary mapping entity UIDs to their graphics items.
        _debug_segment_item_registry: Dictionary mapping segment UIDs to debug items.
        _car_model: The list model containing car entities.
        _road_model: The list model containing road entities.
    """

    def __init__(
        self,
        application_controller: ApplicationController,
        parent=None,
    ) -> None:
        """
        Initialize the traffic scene with configured bounds and model connections.

        Args:
            application_controller: The central controller providing access to
                models and event handlers.
            parent: The parent QObject. Defaults to None.
        """
        super().__init__(parent)

        size = DIMENSION.SCENE_SIZE
        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

        self._application_controller = application_controller
        self._item_registry = {}
        self._debug_segment_item_registry = {}

        view_models = application_controller.view_event_handler.view_models
        self._car_model = view_models.car_list_model
        self._road_model = view_models.road_list_model

        self._connect_model_signals()

    def _connect_model_signals(self) -> None:
        """Connect to model signals to observe entity changes."""
        self._car_model.rowsInserted.connect(self._on_cars_added)
        self._car_model.rowsAboutToBeRemoved.connect(self._on_cars_removed)
        self._car_model.dataChanged.connect(self._on_car_data_changed)

        self._road_model.rowsInserted.connect(self._on_roads_added)
        self._road_model.rowsAboutToBeRemoved.connect(self._on_roads_removed)
        self._road_model.dataChanged.connect(self._on_road_data_changed)

    # -------------------------------------------------------------------------
    # Car Model Handlers
    # -------------------------------------------------------------------------

    def _on_cars_added(self, parent: QModelIndex, first: int, last: int) -> None:
        """
        Handle cars being added to the model.

        Creates CarItem graphics items for each new car and registers them
        as position listeners on their assigned road.

        Args:
            parent: The parent model index (unused for flat lists).
            first: Index of the first inserted row.
            last: Index of the last inserted row (inclusive).
        """
        for row in range(first, last + 1):
            car_entity = self._car_model.get_entity_at(row)
            road_item = self._item_registry[car_entity.lane.road_uid]

            graphics_item = CarItem(
                car_entity, road_item, self._application_controller
            )
            self.addItem(graphics_item)
            self._item_registry[car_entity.uid] = graphics_item
            road_item.add_position_listener(graphics_item)

    def _on_car_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles,
    ) -> None:
        """
        Handle car property changes in the model.

        Updates the corresponding CarItem graphics and handles road reassignment
        if the car moved to a different road.

        Args:
            top_left: Top-left index of the changed range.
            bottom_right: Bottom-right index of the changed range.
            roles: List of changed roles (unused).
        """
        for row in range(top_left.row(), bottom_right.row() + 1):
            updated_car = self._car_model.get_entity_at(row)
            car_item = self._item_registry.get(updated_car.uid)

            if car_item is None:
                continue

            old_car = car_item.data(0)

            if old_car.lane.road_uid != updated_car.lane.road_uid:
                old_road_item = self._item_registry[old_car.lane.road_uid]
                new_road_item = self._item_registry[updated_car.lane.road_uid]

                old_road_item.remove_position_listener(car_item)
                new_road_item.add_position_listener(car_item)

            new_road_item = self._item_registry[updated_car.lane.road_uid]
            car_item.update_data(updated_car, new_road_item)

    def _on_cars_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        """
        Handle cars being removed from the model.

        Removes the corresponding CarItem graphics items and unregisters them
        from position listeners. Called before rows are actually removed.

        Args:
            parent: The parent model index (unused for flat lists).
            first: Index of the first row being removed.
            last: Index of the last row being removed (inclusive).
        """
        for row in range(first, last + 1):
            car_entity = self._car_model.get_entity_at(row)
            car_item = self._item_registry.get(car_entity.uid)

            if car_item is None:
                continue

            road_item = self._item_registry.get(car_entity.lane.road_uid)
            if road_item:
                road_item.remove_position_listener(car_item)

            self.removeItem(car_item)
            del self._item_registry[car_entity.uid]

    # -------------------------------------------------------------------------
    # Road Model Handlers
    # -------------------------------------------------------------------------

    def _on_roads_added(self, parent: QModelIndex, first: int, last: int) -> None:
        """
        Handle roads being added to the model.

        Creates RoadItem graphics items for each new road, checks for crossings
        with existing roads, and reassigns any orphaned cars to their road items.

        Args:
            parent: The parent model index (unused for flat lists).
            first: Index of the first inserted row.
            last: Index of the last inserted row (inclusive).
        """
        for row in range(first, last + 1):
            road_entity = self._road_model.get_entity_at(row)
            graphics_item = RoadItem(road_entity, self._application_controller)

            self.addItem(graphics_item)
            self._item_registry[road_entity.uid] = graphics_item

            self._check_and_create_crossings(graphics_item)
            self._reassign_orphaned_cars(road_entity, graphics_item)

        self._refresh_debug_segments()

    def _reassign_orphaned_cars(self, road_entity, road_item: RoadItem) -> None:
        """
        Reassign cars that belong to the given road to the new road item.

        When a road is added, any existing cars assigned to that road need
        to be updated with the new road item reference.

        Args:
            road_entity: The newly added road entity.
            road_item: The RoadItem graphics item for the road.
        """
        for item in self._item_registry.values():
            if isinstance(item, CarItem):
                car_entity = item.data(0)
                if car_entity.lane.road_uid == road_entity.uid:
                    item.update_data(car_entity, road_item)
                    road_item.add_position_listener(item)

    def _on_road_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles,
    ) -> None:
        """
        Handle road property changes in the model.

        Updates the corresponding RoadItem graphics items when road properties
        (position, lanes, etc.) change.

        Args:
            top_left: Top-left index of the changed range.
            bottom_right: Bottom-right index of the changed range.
            roles: List of changed roles (unused).
        """
        for row in range(top_left.row(), bottom_right.row() + 1):
            road_entity = self._road_model.get_entity_at(row)
            road_item = self._item_registry.get(road_entity.uid)

            if road_item is not None:
                road_item.update_data(road_entity)

        self._refresh_debug_segments()

    def _on_roads_removed(self, parent: QModelIndex, first: int, last: int) -> None:
        """
        Handle roads being removed from the model.

        Removes the corresponding RoadItem graphics items and any crossings
        associated with them. Called before rows are actually removed.

        Args:
            parent: The parent model index (unused for flat lists).
            first: Index of the first row being removed.
            last: Index of the last row being removed (inclusive).
        """
        for row in range(first, last + 1):
            road_entity = self._road_model.get_entity_at(row)
            road_item = self._item_registry.get(road_entity.uid)

            if road_item is None:
                continue

            for listener in list(road_item.position_listeners):
                if isinstance(listener, CrossingItem):
                    self._remove_crossing(listener)

            del self._item_registry[road_entity.uid]
            self.removeItem(road_item)

        self._refresh_debug_segments()

    # -------------------------------------------------------------------------
    # Crossing Management
    # -------------------------------------------------------------------------

    def _check_and_create_crossings(self, new_road_item: RoadItem) -> None:
        """
        Create crossing items where the new road intersects with existing roads.

        Crossings are created between roads of perpendicular orientations
        (horizontal and vertical).

        Args:
            new_road_item: The newly added RoadItem to check for crossings.
        """
        new_orientation = new_road_item.data(0).orientation

        for existing_item in self._item_registry.values():
            if not isinstance(existing_item, RoadItem):
                continue

            existing_orientation = existing_item.data(0).orientation
            if existing_orientation != new_orientation:
                self._create_crossing(new_road_item, existing_item)

    def _create_crossing(self, road_a: RoadItem, road_b: RoadItem) -> None:
        """
        Create a crossing item at the intersection of two roads.

        The crossing is registered as a position listener on both roads
        so it updates when either road moves.

        Args:
            road_a: The first road item.
            road_b: The second road item.
        """
        crossing = CrossingItem(road_a, road_b)
        self.addItem(crossing)

        road_a.add_position_listener(crossing)
        road_b.add_position_listener(crossing)

    def _remove_crossing(self, crossing: CrossingItem) -> None:
        """
        Remove a crossing item and unregister it from its connected roads.

        Args:
            crossing: The crossing item to remove.
        """
        crossing.road_1.remove_position_listener(crossing)
        crossing.road_2.remove_position_listener(crossing)
        self.removeItem(crossing)

    # -------------------------------------------------------------------------
    # Debug Segments
    # -------------------------------------------------------------------------

    def _refresh_debug_segments(self) -> None:
        """
        Refresh debug segment visualization.

        Removes all existing debug segment items and recreates them based on
        the current segment state from the traffic snapshot reader.
        """
        for debug_item in self._debug_segment_item_registry.values():
            self.removeItem(debug_item)
        self._debug_segment_item_registry.clear()

        snapshot_reader = self._application_controller.get_traffic_snapshot_reader()
        segments = snapshot_reader.debug_get_segments()

        for segment in segments.values():
            item = DebugSegmentItem(segment, self._application_controller)
            self._debug_segment_item_registry[segment.uid] = item
            self.addItem(item)
