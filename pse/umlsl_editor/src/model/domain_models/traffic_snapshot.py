from typing import Any, Optional

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.model.helper.observables import ObservableDict, ObservableList, Observable
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter


class TrafficSnapshotValidationError(ValueError):
    pass

class TrafficSnapshot(Observable, TrafficSnapshotReader, TrafficSnapshotWriter):
    """
    Represents the complete state of a traffic simulation.

    Serves as the single source of truth for all roads and cars. Implements both
    TrafficSnapshotReader and TrafficSnapshotWriter interfaces for read/write access.

    Uses Observable pattern to notify observers of changes without PySide dependencies.

    Events:
        - TrafficSnapshotEventType.CAR_ADDED: Fired when a car is added (data: Car)
        - TrafficSnapshotEventType.CAR_REMOVED: Fired when a car is removed (data: Car)
        - TrafficSnapshotEventType.CAR_UPDATED: Fired when a car is updated (data: Car)
        - TrafficSnapshotEventType.ROAD_ADDED: Fired when a road is added (data: Road)
        - TrafficSnapshotEventType.ROAD_REMOVED: Fired when a road is removed (data: Road)
        - TrafficSnapshotEventType.ROAD_UPDATED: Fired when a road is updated (data: Road)
        - TrafficSnapshotEventType.CROSSING_SEGMENT_ADDED: Fired when a crossing segment is added (data: CrossingSegment)
        - TrafficSnapshotEventType.CROSSING_SEGMENT_REMOVED: Fired when a crossing segment is removed (data: CrossingSegment)
        - TrafficSnapshotEventType.CROSSING_SEGMENT_UPDATED: Fired when a crossing segment is updated (data: CrossingSegment)
    """

    def update_road(self, road_data: Road) -> None:
        raise NotImplementedError

    def update_car(self, car_data: Car) -> None:
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

    def get_max_velocity(self) -> float:
        raise NotImplementedError

    def add_road(self, road: Road) -> None:
        raise NotImplementedError

    def remove_road(self, road_name: str) -> None:
        raise NotImplementedError

    def add_car(self, car: Car) -> None:
        self._cars[car.name] = car

    def remove_car(self, car_name: str) -> None:
        raise NotImplementedError

    def __init__(
            self,
            roads: Optional[ObservableDict[str, Road]] = None,
            cars: Optional[ObservableDict[str, Car]] = None,
            crossing_segments: Optional[ObservableList[CrossingSegment]] = None,
    ):
        super().__init__()

        self._roads = ObservableDict[str,Road](
            on_add=lambda road: self.notify(TrafficSnapshotEventType.ROAD_ADDED, road),
            on_remove=lambda road: self.notify(TrafficSnapshotEventType.ROAD_REMOVED, road),
            on_update=lambda road: self.notify(TrafficSnapshotEventType.ROAD_UPDATED, road)
        ) if roads is not None else {}

        self._cars = ObservableDict[str, Car](
            on_add=lambda car: self.notify(TrafficSnapshotEventType.CAR_ADDED, car),
            on_remove=lambda car: self.notify(TrafficSnapshotEventType.CAR_REMOVED, car),
            on_update=lambda car: self.notify(TrafficSnapshotEventType.CAR_UPDATED, car)
        ) if cars is not None else {}

        self._crossing_segments = ObservableList[CrossingSegment](
            on_add=lambda segment: self.notify(TrafficSnapshotEventType.CROSSING_SEGMENT_ADDED, segment),
            on_remove=lambda segment: self.notify(TrafficSnapshotEventType.CROSSING_SEGMENT_REMOVED, segment),
            on_update=lambda segment: self.notify(TrafficSnapshotEventType.CROSSING_SEGMENT_UPDATED, segment)
        ) if cars is not None else {}

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
