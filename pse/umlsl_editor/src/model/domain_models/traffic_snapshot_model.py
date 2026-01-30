from typing import Any, Optional

from sortedcontainers import SortedDict

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.model.helper.uid_service import generate_uid
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.helper.observables import ObservableDict, Observable, ReadOnlyDictView
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_validator import TrafficSnapshotValidator
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


class TrafficSnapshotModel(Observable, TrafficSnapshotReader, TrafficSnapshotWriter):
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
        # - TrafficSnapshotEventType.CROSSING_SEGMENT_ADDED: Fired when a crossing segment is added (data: CrossingSegment)
        # - TrafficSnapshotEventType.CROSSING_SEGMENT_REMOVED: Fired when a crossing segment is removed (data: CrossingSegment)
        # - TrafficSnapshotEventType.CROSSING_SEGMENT_UPDATED: Fired when a crossing segment is updated (data: CrossingSegment)
    """

    def __init__(
            self,
            roads: Optional[ObservableDict[str, Road]] = None,
            cars: Optional[ObservableDict[str, Car]] = None,
    ):

        super().__init__()
        self._cars = cars if cars is not None else ObservableDict[str, Car](
            on_add=lambda car: self.notify(TrafficSnapshotEventType.CAR_ADDED, car),
            on_remove=lambda car: self.notify(TrafficSnapshotEventType.CAR_REMOVED, car),
            on_update=lambda car: self.notify(TrafficSnapshotEventType.CAR_UPDATED, car)
        )

        self._horizontal_roads: ObservableDict[str, Road] = ObservableDict(
            on_add=self._on_road_added,
            on_remove=self._on_road_removed,
            on_update=self._on_road_updated
        )
        self._vertical_roads: ObservableDict[str, Road] = ObservableDict(
            on_add=self._on_road_added,
            on_remove=self._on_road_removed,
            on_update=self._on_road_updated
        )
        self._crossing_segments: ObservableDict[str, CrossingSegment] = ObservableDict()
        """Dictionary of crossing segments, keyed by horizontal lane UID + vertical lane UID."""
        self._lane_segments: ObservableDict[str, LaneSegment] = ObservableDict()
        """Dictionary of lane segments, keyed by lane UID + start road UID + end road UID."""

        self._read_only_roads = ReadOnlyDictView(self._horizontal_roads + self._vertical_roads)
        """Read-only view of the roads dictionary."""
        self._read_only_cars = ReadOnlyDictView(self._cars)
        """Read-only view of the cars dictionary."""

        self.validator = TrafficSnapshotValidator(self)

    @property
    def cars(self):
        return self._read_only_cars

    @property
    def roads(self):
        return self._read_only_roads

    def _on_road_added(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_ADDED, road)

    def _on_road_removed(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_REMOVED, road)

    def _on_road_updated(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_UPDATED, road)
        self.validator.validate_road(road, False)

    def get_cars_on_road(self, road: Road) -> list[Car]:
        pass

    def get_cars(self) -> list[Car]:
        pass

    def get_roads(self) -> list[Road]:
        pass

    def get_cars_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Car]:
        pass

    def get_roads_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Road]:
        pass

    def get_max_velocity(self) -> float:
        pass

    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool:
        pass

    def add_road(self, road: Road) -> None:
        self.validator.validate_road(road, True)
        if road.orientation == RoadOrientation.HORIZONTAL:
            self._horizontal_roads[road.uid] = road
        else:
            self._vertical_roads[road.uid] = road

    def remove_road(self, road_uid: str) -> None:
        if road_uid in self._horizontal_roads:
            self._horizontal_roads.pop(road_uid)
        elif road_uid in self._vertical_roads:
            self._vertical_roads.pop(road_uid)

    def update_road(self, road: Road) -> None:
        self.validator.validate_road(road, False)
        if road.uid in self._horizontal_roads:
            if road.orientation != RoadOrientation.HORIZONTAL:
                self._horizontal_roads.pop(road.uid)
                self._vertical_roads[road.uid] = road
            else:
                self._horizontal_roads[road.uid] = road
        elif road.uid in self._vertical_roads:
            if road.orientation != RoadOrientation.HORIZONTAL:
                self._vertical_roads.pop(road.uid)
                self._horizontal_roads[road.uid] = road
            else:
                self._vertical_roads[road.uid] = road


    def add_car(self, car: Car) -> None:
        self.validator.validate_car(car, True)
        self._cars[car.name] = car

    def remove_car(self, car_name: str) -> None:
        self._cars.pop(car_name)

    def update_car(self, car_data: Car) -> None:
        self.validator.validate_car(car_data, False)
        pass

    def _recalculate_segments(self, car: Car) -> None:
        """Recalculates the segments for a given car based on its current position."""
        raise NotImplementedError

    def _recalculate_static_segments(self):
        """Recalculates all static segments (lane segments and crossing segments) in the traffic snapshot."""
        sorted_horizontal_roads_by_y = sorted(self._horizontal_roads.values(), key=lambda item: item.position)
        sorted_vertical_roads_by_x = sorted(self._vertical_roads.values(), key=lambda item: item.position)

        self._crossing_segments = ObservableDict[str, CrossingSegment]()
        self._lane_segments = ObservableDict[str, LaneSegment]()
        ordered_horizontal_lanes : list[Lane] = []
        ordered_vertical_lanes : list[Lane] = []
        for horizontal_road in sorted_horizontal_roads_by_y:
            ordered_horizontal_lanes += sorted(horizontal_road.backward_lanes + horizontal_road.forward_lanes, key=lambda lane: lane.lane_index)
        for vertical_road in sorted_vertical_roads_by_x:
             ordered_vertical_lanes += sorted(vertical_road.backward_lanes + vertical_road.forward_lanes, key=lambda lane: lane.lane_index)

        previous_horizontal_lane: Lane|None = None
        previous_vertical_lane: Lane|None = None
        for horizontal_lane in ordered_horizontal_lanes:
            for vertical_lane in ordered_vertical_lanes:
                crossing_segment_uid = generate_uid()
                # top_lane_segment = LaneSegment
                # crossing_segment = CrossingSegment(uid= crossing_segment_uid,horizontal_lane=horizontal_lane, vertical_lane=vertical_lane, top_segment_uid=previous_horizontal_lane.u )
                # self._crossing_segments[crossing_segment.uid] = crossing_segment


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
    def from_dict(cls, data: dict[str, Any]) -> "TrafficSnapshotModel":
        """
        Creates a TrafficSnapshot instance from a dictionary.

        Args:
            data: A dictionary containing 'roads' and 'cars' keys.
        """
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_string: str) -> "TrafficSnapshotModel":
        """
        Creates a TrafficSnapshot instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing traffic snapshot data.

        """
        raise NotImplementedError


