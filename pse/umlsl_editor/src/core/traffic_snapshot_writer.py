from abc import ABC, abstractmethod

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road


class TrafficSnapshotWriter(ABC):
    """Interface for writing data into the TrafficSnapshot. Use always this class to mutate the snapshot. NEVER mutate the data models directly."""

    @abstractmethod
    def add_road(self, road: Road) -> None:
        pass

    @abstractmethod
    def remove_road(self, road: Road) -> None:
        """
        Removes a road from the snapshot. Also removes all cars on that road.
        """
        pass

    @abstractmethod
    def add_car(self, car: Car) -> None:
        pass

    @abstractmethod
    def remove_car(self, car: Car) -> None:
        """
        Removes a car from the snapshot.
        """
        pass
