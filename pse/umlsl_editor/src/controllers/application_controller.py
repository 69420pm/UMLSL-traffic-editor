"""The central application controller for the Model-View-Controller architecture"""
from typing import Optional

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
        color:  str,
        position_on_lane:  float,
        transition:  float,
        velocity:  float,
        length:  float,
        next_turn:  TurnIntent) -> bool:
        """
        Adds a car to the traffic snapshot based on the given parameters.

        Args:
            name: Unique human-readable identifier for the car.
            assigned_road: Reference to the Road the car is currently traveling on.
            lane_index: Index of the lane the car is currently in.
            lane_direction: Direction of the lane the car is currently in.
            color: Hex color code
            position_on_lane: Distance along lane
            transition: Lane change progress
            velocity: Current speed
            length: Physical length
            next_turn: Turn intent at intersection

        Returns:
            True if the car was successfully added, False otherwise.
        """
        # create CarParams
        # create the AddCarCommand, execute it and return the result
        raise NotImplementedError("Method not implemented yet.")


