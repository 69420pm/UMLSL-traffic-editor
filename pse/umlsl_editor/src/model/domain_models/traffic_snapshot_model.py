from typing import Any, Optional, Mapping, Iterator, KeysView, ValuesView, ItemsView

from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.entities.road import Road, LaneDirection, RoadParams
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.helper.observables import ObservableDict, ObservableList, Observable
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_validator import TrafficSnapshotValidator


class ReadOnlyDictView(Mapping[str, Any]):
    """
    A read-only view over an ObservableDict that properly wraps its internal dictionary.
    
    This provides a true read-only Mapping interface by delegating to the internal
    _data dict of the ObservableDict, ensuring immutability while maintaining
    compatibility with the Observable pattern.
    """
    
    def __init__(self, observable_dict: ObservableDict):
        """
        Initialize a read-only view.
        
        Args:
            observable_dict: The ObservableDict to create a read-only view over
        """
        self._observable_dict = observable_dict
    
    def __getitem__(self, key: str) -> Any:
        """Get an item by key from the underlying dict."""
        return self._observable_dict._data[key]
    
    def __iter__(self) -> Iterator[str]:
        """Iterate over keys in the underlying dict."""
        return iter(self._observable_dict._data)
    
    def __len__(self) -> int:
        """Return the number of items in the underlying dict."""
        return len(self._observable_dict._data)
    
    def __contains__(self, key: object) -> bool:
        """Check if key exists in the underlying dict."""
        return key in self._observable_dict._data
    
    def keys(self) -> KeysView[str]:
        """Return keys view of the underlying dict."""
        return self._observable_dict._data.keys()
    
    def values(self) -> ValuesView[Any]:
        """Return values view of the underlying dict."""
        return self._observable_dict._data.values()
    
    def items(self) -> ItemsView[str, Any]:
        """Return items view of the underlying dict."""
        return self._observable_dict._data.items()


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
        - TrafficSnapshotEventType.CROSSING_SEGMENT_ADDED: Fired when a crossing segment is added (data: CrossingSegment)
        - TrafficSnapshotEventType.CROSSING_SEGMENT_REMOVED: Fired when a crossing segment is removed (data: CrossingSegment)
        - TrafficSnapshotEventType.CROSSING_SEGMENT_UPDATED: Fired when a crossing segment is updated (data: CrossingSegment)
    """

    def __init__(
            self,
            roads: Optional[ObservableDict[str, Road]] = None,
            cars: Optional[ObservableDict[str, Car]] = None,
    ):
        super().__init__()

        self._roads = roads if roads is not None else ObservableDict[str, Road](
            on_add=lambda road: self.notify(TrafficSnapshotEventType.ROAD_ADDED, road),
            on_remove=lambda road: self.notify(TrafficSnapshotEventType.ROAD_REMOVED, road),
            on_update=lambda road: self.notify(TrafficSnapshotEventType.ROAD_UPDATED, road)
        )

        self._cars = cars if cars is not None else ObservableDict[str, Car](
            on_add=lambda car: self.notify(TrafficSnapshotEventType.CAR_ADDED, car),
            on_remove=lambda car: self.notify(TrafficSnapshotEventType.CAR_REMOVED, car),
            on_update=lambda car: self.notify(TrafficSnapshotEventType.CAR_UPDATED, car)
        )

        self._crossing_segments = ObservableList[CrossingSegment](
            on_add=lambda segment: self.notify(TrafficSnapshotEventType.CROSSING_SEGMENT_ADDED, segment),
            on_remove=lambda segment: self.notify(TrafficSnapshotEventType.CROSSING_SEGMENT_REMOVED, segment),
            on_update=lambda segment: self.notify(TrafficSnapshotEventType.CROSSING_SEGMENT_UPDATED, segment)
        )

        self._read_only_roads = ReadOnlyDictView(self._roads)
        """Read-only view of the roads dictionary."""
        self._read_only_cars = ReadOnlyDictView(self._cars)
        """Read-only view of the cars dictionary."""

        self.validator = TrafficSnapshotValidator(self)

    def get_cars_on_road(self, road: Road) -> list[Car]:
        pass

    def get_car_by_name(self, name: str) -> Car:
        return self._cars.get(name)

    def get_road_by_name(self, name: str) -> Road:
        return self._roads.get(name)

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
        self._roads[road.name] = road

    def remove_road(self, road_name: str) -> None:
        self._roads.pop(road_name)

    def update_road(self, road_data: Road, road_params: RoadParams) -> None:
        self.validator.validate_road(road_data, False)
        if road_params.orientation is not None:
            road_data.orientation = road_params.orientation
        if road_params.forward_lanes is not None:
            road_data.forward_lanes = road_params.forward_lanes
        if road_params.backward_lanes is not None:
            road_data.backward_lanes = road_params.backward_lanes
        if road_params.position is not None:
            road_data.position = road_params.position
        raise NotImplementedError("Prototype Method")

    def add_car(self, car: Car) -> None:
        self.validator.validate_car(car, True)
        self._cars[car.name] = car

    def remove_car(self, car_name: str) -> None:
        self._cars.pop(car_name)

    def update_car(self, car_data: Car, car_params: CarParams) -> None:
        self.validator.validate_car(car_data, False)
        if car_params.color is not None:
            car_data.color = car_params.color
        if car_params.length is not None:
            car_data.length = car_params.length
        if car_params.acceleration is not None:
            car_data.acceleration = car_params.acceleration
        if car_params.velocity is not None:
            car_data.velocity = car_params.velocity
        raise NotImplementedError("Prototype Method")

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

    @property
    def cars(self):
        return self._read_only_cars

    @property
    def roads(self):
        return self._read_only_roads
