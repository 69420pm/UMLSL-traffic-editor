"""The central application controller for the Model-View-Controller architecture"""
from typing import Optional

from pse.umlsl_editor.src.commands.add_car import AddCarCommand
from pse.umlsl_editor.src.core.dataclasses.params import CarParams
from pse.umlsl_editor.src.core.dataclasses.road import Road, LaneDirection
from pse.umlsl_editor.src.core.dataclasses.turn_intent import TurnIntent


class ApplicationController:
    def __init__(self):
        pass

    def add_car(
        self,
        name: str,
        assigned_road: Road,
        lane_index: int,
        lane_direction: LaneDirection,
        color: Optional[str] = None,
        position_on_lane: Optional[float] = None,
        transition: Optional[float] = None,
        velocity: Optional[float] = None,
        length: Optional[float] = None,
        next_turn: Optional[TurnIntent] = None,) -> bool:
        """
        Adds a car to the traffic snapshot based on the given parameters.

        Args:
            name: Unique human-readable identifier for the car.
            assigned_road: Reference to the Road the car is currently traveling on.
            lane_index: Index of the lane the car is currently in.
            lane_direction: Direction of the lane the car is currently in.
            color: Hex color code (default: "#FF0000" if not provided).
            position_on_lane: Distance along lane (default: 0.0 if not provided).
            transition: Lane change progress (default: 0.0 if not provided).
            velocity: Current speed (default: 0.0 if not provided).
            length: Physical length (default: 4.0 if not provided).
            next_turn: Turn intent at intersection (default: None if not provided).

        Returns:
            True if the car was successfully added, False otherwise.
        """
        car_params = CarParams()
        car_params.name = name
        car_params.assigned_road = assigned_road
        car_params.lane_index = lane_index
        car_params.lane_direction = lane_direction

        if color is not None:
            car_params.color = color
        if position_on_lane is not None:
            car_params.position_on_lane = position_on_lane
        if transition is not None:
            car_params.transition = transition
        if velocity is not None:
            car_params.velocity = velocity
        if length is not None:
            car_params.length = length
        if next_turn is not None:
            car_params.next_turn = next_turn

        # create the AddCarCommand, execute it and return the result
        raise NotImplementedError("Method not implemented yet.")


