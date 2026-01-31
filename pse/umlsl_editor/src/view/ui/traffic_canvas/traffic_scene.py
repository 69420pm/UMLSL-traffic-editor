"""
Traffic scene for the UMLSL Traffic Editor.

Manages the QGraphicsScene containing all traffic entities (roads, cars, crossings).
"""

from PySide6.QtCore import QRectF, QModelIndex
from PySide6.QtWidgets import QGraphicsScene

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.car_item import CarItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.crossing_item import (
    CrossingItem,
)
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.view_constants import DIMENSION


class TrafficScene(QGraphicsScene):
    """
    Graphics scene containing all traffic entities.

    Manages the visual representation of roads, cars, and crossings.
    Provides a registry for tracking items and a cache for road data.
    """

    def __init__(self, application_controller: ApplicationController, parent=None) -> None:
        """Initialize the traffic scene with configured bounds."""
        super().__init__(parent)

        # Set up scene bounds
        size = DIMENSION.SCENE_SIZE
        self.setSceneRect(QRectF(-size / 2, -size / 2, size, size))

        self.data_controller = application_controller.data_controller

        self.car_model = self.data_controller.get_view_models().car_list_model
        self.road_model = self.data_controller.get_view_models().road_list_model

        self._item_registry = {}

        self.car_model.rowsInserted.connect(self._on_cars_added)
        self.car_model.rowsAboutToBeRemoved.connect(self._on_cars_removed)
        self.car_model.dataChanged.connect(self._on_car_data_changed)

    def _on_cars_added(self, parent: QModelIndex, first: int, last: int) -> None:
        """Called when cars are added to the list model."""
        for row in range(first, last + 1):
            car_entity = self.car_model.get_entity_at(row)
            graphics_item = CarItem(car_entity, self.data_controller)
            self.addItem(graphics_item)
            self._item_registry[car_entity.uid] = graphics_item
            self._item_registry[car_entity.lane.road_uid].add_position_listener(graphics_item)

    def _on_cars_removed(self, parent: QModelIndex, first: int, last: int):
        """Called BEFORE cars are removed from the list model."""
        for row in range(first, last + 1):
            car_entity = self.car_model.get_entity_at(row)

            if car_entity in self._item_registry:
                item = self._item_registry[car_entity]
                self._item_registry[car_entity.lane.road_uid].remove_position_listener(item)
                self.removeItem(item)
                del self._item_registry[car_entity]

    def _on_car_data_changed(self, top_left: QModelIndex, bottom_right: QModelIndex, roles):
        """Called when a car's property (e.g., position) changes."""
        for row in range(top_left.row(), bottom_right.row() + 1):
            car_entity = self.car_model.get_entity_at(row)

            if car_entity in self._item_registry:
                old_car_entity = self._item_registry[car_entity.uid]
                item = self._item_registry[car_entity]

                # If the car changed roads, update road listeners
                if old_car_entity.lane.road_uid != car_entity.lane.road_uid:
                    self._item_registry[old_car_entity.lane.road_uid].remove_position_listener(item)
                    self._item_registry[car_entity.lane.road_uid].add_position_listener(item)

                item.update_visuals()

    def _on_roads_added(self, parent: QModelIndex, first: int, last: int) -> None:
        for row in range(first, last + 1):
            road_entity = self.road_model.get_entity_at(row)
            graphics_item = RoadItem(road_entity)
            self.addItem(graphics_item)
            self._item_registry[road_entity.uid] = graphics_item
            self._check_and_create_crossings(graphics_item)

    def _check_and_create_crossings(self, new_road_item: RoadItem):
        """Finds perpendicular roads and creates crossings."""
        new_orientation = new_road_item.data(0).orientation

        for existing_road in self.data_controller.get_all_roads().values():
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

    def _remove_listener_from_roads(self, graphics_item):
        """Removes a graphics item from all road listener lists."""
        for road in self.data_controller.get_all_roads().values():
            if graphics_item in self._item_registry:
                road_item = self._item_registry[graphics_item]
                road_item.remove_position_listener(graphics_item)
