from abc import ABC, abstractmethod
from typing import Any

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery


class TrafficView(ABC):
    """
    Abstract interface for the traffic simulation view.
    Allows the controller to interact with the view without knowing the specific implementation (2D, 3D, etc.).
    """

    @abstractmethod
    def initialize_view(self) -> None:
        """Initializes the entire traffic view from ground up. Gets also called when loading a new traffic snapshot."""
        pass

    @abstractmethod
    def add_car_view(self, car_data: Car) -> None:
        """Adds a visual representation of a car."""
        pass

    @abstractmethod
    def remove_car_view(self, car_data: Car) -> None:
        """Removes the visual representation of a car."""
        pass

    @abstractmethod
    def update_car_view(self, car_data: Car) -> None:
        """Updates the visual representation of a car."""
        pass

    @abstractmethod
    def add_road_view(self, road_data: Road) -> None:
        """Adds a visual representation of a road."""
        pass

    @abstractmethod
    def remove_road_view(self, road_data: Road) -> None:
        """Removes the visual representation of a road."""
        pass

    @abstractmethod
    def update_road_view(self, road_data: Road) -> None:
        """Updates the visual representation of a road."""
        pass

    @abstractmethod
    def add_crossing_segment_view(self, crossing_segment_data: CrossingSegment) -> None:
        """Adds a visual representation of a crossing_segment."""
        pass

    @abstractmethod
    def remove_crossing_segment_view(self, crossing_segment_data: CrossingSegment) -> None:
        """Removes the visual representation of a crossing_segment."""
        pass

    @abstractmethod
    def update_crossing_segment_view(self, crossing_segment_data: CrossingSegment) -> None:
        """Updates the visual representation of a crossing_segment."""
        pass

    @abstractmethod
    def add_umlsl_query_view(self, umlsl_query_data: UMLSLQuery) -> None:
        """Adds a visual representation of a UMLSL query."""
        pass

    @abstractmethod
    def remove_umlsl_query_view(self, road_data: Any) -> None:
        """Removes the visual representation of a UMLSL query."""
        pass

    @abstractmethod
    def update_umlsl_query_view(self, road_data: Any) -> None:
        """Updates the visual representation of a UMLSL query."""
        pass

    @abstractmethod
    def select_car_view(self, car_data: Car) -> None:
        """Selects the visual representation of a car."""
        pass

    @abstractmethod
    def deselect_car_view(self, car_data: Car) -> None:
        """Deselects the visual representation of a car."""
        pass

    @abstractmethod
    def select_road_view(self, road_data: Road) -> None:
        """Selects the visual representation of a road."""
        pass

    @abstractmethod
    def deselect_road_view(self, road_data: Road) -> None:
        """Deselects the visual representation of a road."""
        pass

    @abstractmethod
    def change_breaking_acceleration(self) -> None:
        """Changes the breaking acceleration of the cars."""
        pass

    @abstractmethod
    def toggle_coordinate_system(self) -> None:
        """Changes the rendering of the coordinate system."""
        pass

    @abstractmethod
    def toggle_safety_distance(self) -> None:
        """Changes the rendering of the safety distance."""
        pass