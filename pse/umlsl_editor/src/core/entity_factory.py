from typing import Optional

from pse.umlsl_editor.src.core.dataclasses.car import Car, TurnIntent
from pse.umlsl_editor.src.core.dataclasses.road import (
    LaneDirection,
    Road,
    RoadOrientation,
)


class EntityFactory:
    """Creates car and road objects to store in the traffic snapshot."""

    @staticmethod
    def create_car(
        name: str,
        assigned_road: Road,
        lane_index: int,
        lane_direction: LaneDirection,
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
            lane_index: The index of the lane the car is in.
            lane_direction: The direction of the lane (forward or backward).
            color: Hex color code for rendering (default: "#FF0000").
            position_on_lane: Distance along the lane (default: 0.0).
            transition: Lane change progress from -1.0 to 1.0 (exclusive) (default: 0.0).
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
            lane_index=lane_index,
            lane_direction=lane_direction,
            **kwargs,
        )

    @staticmethod
    def create_road(
        name: str,
        orientation: RoadOrientation,
        position: float,
        forward_lanes: Optional[int],
        backward_lanes: Optional[int],
    ) -> Road:
        """Create a Road instance.

        Args:
            name: The unique human readable name of the road.
            orientation: The orientation of the road (horizontal or vertical).
            position: The position of the road in the coordinate system.
            forward_lanes: Number of lanes in the forward direction (default: 0).
            backward_lanes: Number of lanes in the backward direction (default: 0).
        """
        kwargs: dict = {}
        if forward_lanes is not None:
            kwargs["forward_lanes"] = forward_lanes
        if backward_lanes is not None:
            kwargs["backward_lanes"] = backward_lanes
        return Road(name, orientation, position, **kwargs)
