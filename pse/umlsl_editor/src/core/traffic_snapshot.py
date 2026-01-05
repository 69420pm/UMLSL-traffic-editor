from typing import Any, Optional

from PySide6.QtCore import QObject, Signal

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road
from pse.umlsl_editor.src.core.dataclasses.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.core.dataclasses.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.core.traffic_snapshot_observables import ObservableDict, ObservableList
from pse.umlsl_editor.src.core.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.core.traffic_snapshot_writer import TrafficSnapshotWriter


class TrafficSnapshotValidationError(ValueError):
    pass

class TrafficSnapshot(QObject, TrafficSnapshotReader, TrafficSnapshotWriter):
    """
    Represents the complete state of a traffic simulation.

    Serves as the single source of truth for all roads and cars. Implements both
    TrafficSnapshotReader and TrafficSnapshotWriter interfaces for read/write access.
    """

    def update_road(self, road_data: Road) -> None:
        raise NotImplementedError

    def update_car(self, car_data: Car) -> None:
        raise NotImplementedError

    def add_umlsl_query(self, umlsl_query: UMLSLQuery) -> None:
        raise NotImplementedError

    def remove_umlsl_query(self, umlsl_query: UMLSLQuery) -> None:

        raise NotImplementedError()

    def update_umlsl_query(self, umlsl_query_data: UMLSLQuery) -> None:
        raise NotImplementedError

    # Define Signals for Model Changes
    car_added = Signal(Car)
    car_removed = Signal(Car)
    car_updated = Signal(Car)

    road_added = Signal(Road)
    road_removed = Signal(Road)
    road_updated = Signal(Road)

    crossing_segment_added = Signal(CrossingSegment)
    crossing_segment_removed = Signal(CrossingSegment)
    crossing_segment_updated = Signal(CrossingSegment)

    umlsl_query_added = Signal(UMLSLQuery)
    umlsl_query_removed = Signal(UMLSLQuery)
    umlsl_query_updated = Signal(UMLSLQuery)

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

    def remove_road(self, road_name: str) -> None:
        raise NotImplementedError

    def add_car(self, car: Car) -> None:
        raise NotImplementedError

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
            on_add=self.road_added.emit,
            on_remove=self.road_removed.emit,
            on_update=self.road_updated.emit
        ) if roads is not None else {}

        self._cars = ObservableDict[str, Car](
            on_add=self.car_added.emit,
            on_remove=self.car_removed.emit,
            on_update=self.car_updated.emit
        ) if cars is not None else {}

        self._crossing_segments = ObservableList[CrossingSegment](
            on_add=self.crossing_segment_added.emit,
            on_remove=self.crossing_segment_removed.emit,
            on_update=self.crossing_segment_updated.emit
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
