from abc import ABC, abstractmethod

from pse.umlsl_editor.src.core.entities.car import Car
from pse.umlsl_editor.src.core.entities.road import Road
from pse.umlsl_editor.src.core.entities.umlsl_query import UMLSLQuery


class TrafficSnapshotWriter(ABC):
    """Interface for writing data into the TrafficSnapshot. Use always this class to mutate the snapshot. NEVER mutate the data models directly."""

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
    def update_road(self, road_data: Road) -> None:
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
    def update_car(self, car_data: Car) -> None:
        """
        Updates an existing car in the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            TrafficSnapshotValidationError: If the updated car is invalid in the context of the snapshot.
        """
        pass

    @abstractmethod
    def add_umlsl_query(self, umlsl_query: UMLSLQuery) -> None:
        """
        Adds a UMLSL query to the snapshot and validates all attributes in the context of the snapshot.
        Raises:
            TrafficSnapshotValidationError: If the UMLSL query is invalid in the context of the snapshot.
        """
        pass

    @abstractmethod
    def remove_umlsl_query(self, umlsl_query: UMLSLQuery) -> None:
        """
        Removes a UMLSL query from the snapshot.
        """
        pass

    @abstractmethod
    def update_umlsl_query(self, umlsl_query_data: UMLSLQuery) -> None:
        """
        Updates an existing UMLSL query in the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            TrafficSnapshotValidationError: If the updated UMLSL query is invalid in the context of the snapshot.
        """
        pass
