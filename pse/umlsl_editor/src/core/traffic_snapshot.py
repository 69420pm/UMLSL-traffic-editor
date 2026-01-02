from abc import ABC, abstractmethod
from typing import Any, Optional

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road
from pse.umlsl_editor.src.core.traffic_snapshot_observables import ObservableDict
from pse.umlsl_editor.src.core.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.core.traffic_snapshot_writer import TrafficSnapshotWriter


class TrafficSnapshotValidationError(ValueError):
    pass


class Segment(ABC):
    @abstractmethod
    def is_crossing_segment(self) -> bool:
        pass


class LaneSegment(Segment):
    def is_crossing_segment(self) -> bool:
        return False


class CrossingSegment(Segment):
    def is_crossing_segment(self) -> bool:
        return True


class Path:
    def __init__(self, segments: list[Segment]):
        self.segments = segments


class CarSnapshotContext:
    def __init__(self, car: Car):
        self.car = car
        self.reserved_lanes: list[LaneSegment] = []
        self.claimed_lanes: list[LaneSegment] = []
        self.reserved_crossings: list[CrossingSegment] = []
        self.claimed_crossings: list[CrossingSegment] = []
        # todo: path pursued by car
        self.path: Path = Path([])
        # todo: curr : I → Z such that curr(C ) is (the index - we save the object) of the path element of pth(C) currently occupied by the rear of C
        # type of that is an edge
        self.position = car.absolute_position()
        self.speed = car.velocity
        self.accel = 0


class TrafficSnapshot(TrafficSnapshotReader, TrafficSnapshotWriter):
    """
    Represents the complete state of a traffic simulation.

    Serves as the single source of truth for all roads and cars. Implements both
    TrafficSnapshotReader and TrafficSnapshotWriter interfaces for read/write access.
    """

    def get_car_context(self, car: Car) -> CarSnapshotContext:
        raise NotImplementedError

    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool:
        raise NotImplementedError

    def get_cars_on_road(self, road: Road) -> list[Car]:
        raise NotImplementedError

    def get_cars(self) -> list[Car]:
        raise NotImplementedError

    def get_roads(self) -> list[Road]:
        raise NotImplementedError

    def get_cars_in_rectangle(
            self, x_min: float, y_min: float, x_max: float, y_max: float
    ) -> list[Car]:
        raise NotImplementedError

    def get_roads_in_rectangle(
            self, x_min: float, y_min: float, x_max: float, y_max: float
    ) -> list[Road]:
        raise NotImplementedError

    def add_road(self, road: Road) -> None:
        raise NotImplementedError

    def remove_road(self, road: Road) -> None:
        raise NotImplementedError

    def add_car(self, car: Car) -> None:
        raise NotImplementedError

    def remove_car(self, car: Car) -> None:
        raise NotImplementedError

    def __init__(
            self,
            roads: Optional[ObservableDict[str, Road]] = None,
            cars: Optional[ObservableDict[str, Car]] = None,
    ):
        self._roads = dict(roads) if roads is not None else {}
        self._cars = dict(cars) if cars is not None else {}

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the TrafficSnapshot instance to a dictionary suitable for JSON encoding.
        """
        raise NotImplementedError

    def to_json(self) -> str:
        """
        Serializes the TrafficSnapshot instance to a JSON string.
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrafficSnapshot":
        """
        Creates a TrafficSnapshot instance from a dictionary.

        Args:
            data: A dictionary containing 'roads' and 'cars' keys.
        """
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_string: str) -> "TrafficSnapshot":
        """
        Creates a TrafficSnapshot instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing traffic snapshot data.

        """
        raise NotImplementedError
