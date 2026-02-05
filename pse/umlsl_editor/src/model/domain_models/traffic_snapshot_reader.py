from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection

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
    def get_cars(self) -> dict[str, Car]:
        """
        Returns a list of all cars in the snapshot.
        """
        pass

    @abstractmethod
    def get_car_list(self) -> list[Car]:
        """
        Returns the list of cars.
        """
        pass

    @abstractmethod
    def get_car_by_name(self, name: str) -> Car | None:
        """
        Returns the car with the specified name.
        """
        pass

    @abstractmethod
    def get_roads(self) -> dict[str, Road]:
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

    @abstractmethod
    def is_car_existing(self, uid: str) -> bool:
        """
        Checks if a car with the specified UID exists in the snapshot.

        Args:
            uid: The unique identifier of the car.

        Returns:
            True if the car exists, False otherwise.
        """
        pass

    @abstractmethod
    def is_road_existing(self, uid: str) -> bool:
        """
        Checks if a road with the specified UID exists in the snapshot.

        Args:
            uid: The unique identifier of the road.

        Returns:
            True if the road exists, False otherwise.
        """
        pass

    @abstractmethod
    def debug_get_segments(self) -> dict[str, Segment]:
        """
        Returns all segments in the snapshot for debugging purposes.
        """
        pass

    @abstractmethod
    def get_scene_size(self) -> float:
        pass

    @abstractmethod
    def get_valid_turn_intent_lanes(self, car_position: float, car_speed: float, car_lane: Lane, car_length: float,
                                    turn_direction: TurnDirection) -> list[Lane]:
        """
        Returns a valid target lane for the given turn intent, or None if no valid lane exists. A car can't turn into
        a wrong-way lane.

        Args:
            car_position: The current position of the car on its lane.
            car_speed: The current speed of the car to determine in which direction the car is driving.
            car_length: The length of the car
            car_lane: The current lane of the car.
            turn_direction: The intended turn direction (LEFT or RIGHT).

        Returns:
            A valid target Lane for the turn intent, or None if no valid lane exists.
        """
        pass

    def get_segment_from_lane_position(self, lane: 'Lane', position_on_lane: float) -> Segment | None:
        pass

    def all_segments(self) -> list[Segment]:
        pass
