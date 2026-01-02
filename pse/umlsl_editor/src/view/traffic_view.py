from abc import ABC, abstractmethod
from typing import Any


class TrafficView(ABC):
    """
    Abstract interface for the traffic simulation view.
    Allows the controller to interact with the view without knowing the specific implementation (2D, 3D, etc.).
    """

    @abstractmethod
    def add_car_view(self, car_data: Any) -> None:
        """Adds a visual representation of a car."""
        pass

    @abstractmethod
    def remove_car_view(self, car_data: Any) -> None:
        """Removes the visual representation of a car."""
        pass

    @abstractmethod
    def update_car_view(self, car_data: Any) -> None:
        """Updates the visual representation of a car."""
        pass

    @abstractmethod
    def add_road_view(self, road_data: Any) -> None:
        """Adds a visual representation of a road."""
        pass

    @abstractmethod
    def remove_road_view(self, road_data: Any) -> None:
        """Removes the visual representation of a road."""
        pass

    @abstractmethod
    def update_road_view(self, road_data: Any) -> None:
        """Updates the visual representation of a road."""
        pass

