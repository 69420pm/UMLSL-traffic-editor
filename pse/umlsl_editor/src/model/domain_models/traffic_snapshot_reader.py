from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery

if TYPE_CHECKING:
    from pse.umlsl_editor.src.model.entities.car import Car
    from pse.umlsl_editor.src.model.entities.road import Road


class TrafficSnapshotReader(ABC):
    """Interface for reading data out of the TrafficSnapshot. Use always this class to read data from the snapshot. NEVER access the data graphic_items directly."""

    @abstractmethod
    def get_cars_on_road(self, road: Road) -> list[Car]:
        pass

    @abstractmethod
    def get_cars(self) -> list[Car]:
        """
        Returns a list of all cars in the snapshot.
        """
        pass

    @abstractmethod
    def get_roads(self) -> list[Road]:
        """
        Returns a list of all roads in the snapshot.
        """
        pass

    @abstractmethod
    def get_car_by_name(self, name: str) -> Car:
        """
        Returns a car by a given name.
        """
        pass

    @abstractmethod
    def get_road_by_name(self, name: str) -> Road:
        """
        Returns a road by a given name.
        """
        pass

    @abstractmethod
    def get_query_by_id(self, query_id: str) -> UMLSLQuery:
        """
        Returns a query by a given name.
        """
        pass

    @abstractmethod
    def get_cars_in_rectangle(
            self, x_min: float, y_min: float, x_max: float, y_max: float
    ) -> list[Car]:
        """
        Returns a list of cars that are located within the specified rectangular area.
        """
        pass

    @abstractmethod
    def get_roads_in_rectangle(
            self, x_min: float, y_min: float, x_max: float, y_max: float
    ) -> list[Road]:
        """
        Returns a list of roads that are located within the specified rectangular area.
        """
        pass

    @abstractmethod
    def get_max_velocity(self) -> float:
        """
        Returns the maximum velocity of all cars in the snapshot.
        """
        pass

    @abstractmethod
    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool:
        """
        Validates if the specified lane index and direction exist on the given road.

        Args:
            road: The road to validate against.
            lane_index: The index of the lane to validate.
            lane_direction: The direction of the lane to validate ('fn' for forward, 'bn' for backward).

        Returns:
            True if the lane index and direction are valid for the road, False otherwise.
        """
        pass
