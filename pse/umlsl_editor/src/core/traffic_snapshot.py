import json
from typing import Any, Optional

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road
from pse.umlsl_editor.src.core.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.core.traffic_snapshot_writer import TrafficSnapshotWriter


class TrafficSnapshot(TrafficSnapshotReader, TrafficSnapshotWriter):
    """
    Represents the complete state of a traffic simulation.

    Serves as the single source of truth for all roads and cars. Implements both
    TrafficSnapshotReader and TrafficSnapshotWriter interfaces for read/write access.
    """

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
        roads: Optional[dict[str, Road]] = None,
        cars: Optional[dict[str, Car]] = None,
    ):
        self._roads = dict(roads) if roads is not None else {}
        self._cars = dict(cars) if cars is not None else {}

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the TrafficSnapshot instance to a dictionary suitable for JSON encoding.

        Returns:
            A dictionary containing:
                - 'roads': A dictionary mapping road names to road dictionaries.
                - 'cars': A dictionary mapping car names to car dictionaries.
        """
        return {
            "roads": {name: road.to_dict() for name, road in self._roads.items()},
            "cars": {name: car.to_dict() for name, car in self._cars.items()},
        }

    def to_json(self) -> str:
        """
        Serializes the TrafficSnapshot instance to a JSON string.

        Returns:
            A JSON-formatted string representation of the TrafficSnapshot.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrafficSnapshot":
        """
        Creates a TrafficSnapshot instance from a dictionary.

        Args:
            data: A dictionary containing 'roads' and 'cars' keys.

        Returns:
            A new TrafficSnapshot instance populated with the provided data.

        Raises:
            ValueError: If required keys are missing or values are invalid.
        """
        if "roads" not in data:
            raise ValueError("Missing required key 'roads' in TrafficSnapshot data")
        if "cars" not in data:
            raise ValueError("Missing required key 'cars' in TrafficSnapshot data")

        # First, deserialize all roads
        roads = {name: Road.from_dict(road_data) for name, road_data in data["roads"].items()}

        # Then, deserialize all cars using the road lookup
        cars = {name: Car.from_dict(car_data, roads) for name, car_data in data["cars"].items()}

        return cls(roads=roads, cars=cars)

    @classmethod
    def from_json(cls, json_string: str) -> "TrafficSnapshot":
        """
        Creates a TrafficSnapshot instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing traffic snapshot data.

        Returns:
            A new TrafficSnapshot instance populated with the parsed JSON data.

        Raises:
            ValueError: If the JSON structure is invalid or values fail validation.
            json.JSONDecodeError: If the string is not valid JSON.
        """
        data = json.loads(json_string)
        return cls.from_dict(data)

