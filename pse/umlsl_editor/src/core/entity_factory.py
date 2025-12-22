from typing import Dict, Optional

from pse.umlsl_editor.src.core.dataclasses.car import Car, TurnIntent
from pse.umlsl_editor.src.core.dataclasses.lane import Lane, LaneDirection
from pse.umlsl_editor.src.core.dataclasses.road import Road, RoadOrientation


class EntityFactory:
    """Creates all car and road objects to store in the traffic snapshot."""

    def __init__(
        self,
    ):
        pass

    @staticmethod
    def createCar(
        name: str,
        assigned_road: Road,
        lane: Lane,
        color: Optional[str] = None,
        position_on_lane: Optional[float] = None,
        transition: Optional[float] = None,
        velocity: Optional[float] = None,
        length: Optional[float] = None,
        next_turn: Optional[TurnIntent] = None,
    ) -> Car:
        """
        Create a Car instance.

        Required arguments must be provided. Optional arguments will use
        the Car class defaults if not specified (i.e., if None).

        Args:
            name: The unique human readable name of the car.
            assigned_road: The road the car is currently on.
            lane: The lane the car is currently in.
            color: Hex color code for rendering (default: "#FF0000").
            position_on_lane: Distance along the lane (default: 0.0).
            transition: Lane change progress from -1.0 to 1.0 (default: 0.0).
            velocity: Current speed (default: 0.0).
            length: Physical length (default: 4.0).
            next_turn: Intended turn at next intersection (default: None).

        Returns:
            A new Car instance.
        """
        kwargs: dict = {}

        if color is not None:
            kwargs["color"] = color
        if position_on_lane is not None:
            kwargs["position_on_lane"] = position_on_lane
        if transition is not None:
            kwargs["transition"] = transition
        if velocity is not None:
            kwargs["velocity"] = velocity
        if length is not None:
            kwargs["length"] = length
        if next_turn is not None:
            kwargs["next_turn"] = next_turn

        return Car(
            name=name,
            assigned_road=assigned_road,
            lane=lane,
            **kwargs,
        )

    @staticmethod
    def create_road(
        name: str,
        orientation: RoadOrientation,
        position: float,
        lanes: list[Lane],
    ) -> Road:
        """Create a Road instance.

        Args:
            name: The unique human readable name of the road.
            orientation: The orientation of the road (horizontal or vertical).
            position: The position of the road in the coordinate system.
            lanes: A list of Lane objects that belong to this road.
        """
        return Road(name, orientation, position, lanes)

    @staticmethod
    def create_lane(index: int, direction: LaneDirection) -> Lane:
        """
        Creates a lane object.

        Args:
            index: The index of the lane counted from the inside out. Index is always dependent on the direction.
            direction: The direction of the lane.

        """

        return Lane(index, direction)
