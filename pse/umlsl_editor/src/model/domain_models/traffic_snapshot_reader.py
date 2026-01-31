from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import Direction
    from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
    from pse.umlsl_editor.src.model.entities.car import Car, CarParams
    from pse.umlsl_editor.src.model.entities.road import Road, RoadParams


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

    @abstractmethod
    def get_lane_width(self):
        """
        Returns the width of lanes in the snapshot.
        """
        pass

    @abstractmethod
    def get_adjacent_segment(self, segment_uid: str, direction: Direction) -> Segment | None:
        """
        Returns the adjacent segment in the specified direction ('left', 'right', 'up', 'down').

        Args:
            segment_uid: The UID of the current segment.
            direction: The direction to find the adjacent segment ('left', 'right', 'up', 'down').
        Returns:
            The adjacent Segment if found, otherwise None.
        """
        pass

    @abstractmethod
    def get_road_by_uid(self, uid: str) -> Road:
        """
        Returns the road with the specified UID, or None if not found.
        """
        pass

    @abstractmethod
    def get_next_road_in_front_of_car(self, car: Car) -> Road | None:
        """
        Returns the next road in front of the specified car

        Args:
            car: The car for which to find the next road in front."""
        pass

    @abstractmethod
    def validate_car_params(self, car_params: CarParams, new_instantiation: bool) -> None:
        """
        Validates the given car parameters.

        Args:
            car_params: The parameters of the car to validate.
            new_instantiation: Whether the car is being newly instantiated.

        Raises:
            ValidationError: If any validation check fails.
        """
        pass

    @abstractmethod
    def validate_road_params(self, road_params: RoadParams, new_instantiation: bool) -> None:
        """
        Validates the given road parameters.

        Args:
            road_params: The parameters of the road to validate.
            new_instantiation: Whether the road is being newly instantiated.

        Raises:
            ValidationError: If any validation check fails.
        """
        pass
