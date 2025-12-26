from typing import Optional

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
