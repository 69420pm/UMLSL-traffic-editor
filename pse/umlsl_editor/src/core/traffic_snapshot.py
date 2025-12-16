from typing import Dict, List, Optional

from pse.umlsl_editor.src.core.car import Car
from pse.umlsl_editor.src.core.road import Road


class TrafficSnapshot:
    """Root data object. Contains all roads with its lanes and cars. Central Manager to use to get state of data models."""

    def __init__(
        self,
        roads: Optional[Dict[str, Road]] = None,
        cars: Optional[Dict[str, Car]] = None,
    ):
        self.roads: Dict[str, Road] = roads if roads is not None else {}
        self.cars: Dict[str, Car] = cars if cars is not None else {}
        # self.queries: List['UMLSLQuery'] = []

    def get_road_by_id(self, road_id: str) -> Optional[Road]:
        """
        Retrieve a road by its identifier.

        Args:
            road_id: The unique identifier of the road to retrieve

        Returns:
            The Road object if found, None otherwise
        """
        pass

    def get_car_by_id(self, car_id: str) -> Optional[Car]:
        """
        Retrieve a car by its identifier.

        Args:
            car_id: The unique identifier of the car to retrieve

        Returns:
            The Car object if found, None otherwise
        """
        pass

    def get_cars_on_road(self, road_id: str) -> Optional[List[Car]]:
        """
        Retrieve all cars currently on a specific road.

        Args:
            road_id: The unique identifier of the road

        Returns:
            A list of Car objects on the specified road
        """
        pass

    def get_cars_in_lane(self, lane_id: str) -> Optional[List[Car]]:
        """
        Retrieve all cars currently in a specific lane.

        Args:
            lane_id: The unique identifier of the lane

        Returns:
            A list of Car objects in the specified lane

        """
        pass

    def add_road(self, road: Road) -> None:
        """
        Add a new road to the traffic snapshot.

        Args:
            road: The Road object to add
        """
        pass

    def add_car(self, car: Car) -> None:
        """
        Add a new car to the traffic snapshot.

        Args:
            car: The Car object to add
        """
        pass

    def remove_road(self, road_id: str) -> None:
        """
        Remove a road from the traffic snapshot with all its lanes and cars.

        Args:
            road_id: The unique identifier of the road to remove
        """
        pass

    def remove_car(self, car_id: str) -> None:
        """
        Remove a car from the traffic snapshot.

        Args:
            car_id: The unique identifier of the car to remove
        """
        pass
