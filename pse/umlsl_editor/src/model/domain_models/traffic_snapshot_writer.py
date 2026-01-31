from abc import ABC, abstractmethod

from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.entities.road import Road, RoadParams


class TrafficSnapshotWriter(ABC):
    """Interface for writing data into the TrafficSnapshot. Use always this class to mutate the snapshot. NEVER mutate the data graphic_items directly."""

    @abstractmethod
    def add_road(self, road: Road) -> None:
        """
        Adds a road to the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            TrafficSnapshotValidationError: If the road is invalid in the context of the snapshot.
        """
        pass

    @abstractmethod
    def remove_road(self, road_name: str) -> None:
        """
        Removes a road from the snapshot. Also removes all cars on that road.
        """
        pass

    @abstractmethod
    def update_road(self, road_data: Road, road_params: RoadParams) -> None:
        """
        Updates an existing road in the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            TrafficSnapshotValidationError: If the updated road is invalid in the context of the snapshot.
        """
        pass

    @abstractmethod
    def add_car(self, car: Car) -> None:
        """
        Adds a car to the snapshot and validates all attributes in the context of the snapshot.
        Raises:
            TrafficSnapshotValidationError: If the car is invalid in the context of the snapshot.
        """
        pass

    @abstractmethod
    def remove_car(self, car_name: str) -> None:
        """
        Removes a car from the snapshot.
        """
        pass

    @abstractmethod
    def update_car(self, car_data: Car, car_params: CarParams) -> None:
        """
        Updates an existing car in the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            TrafficSnapshotValidationError: If the updated car is invalid in the context of the snapshot.
        """
        pass
