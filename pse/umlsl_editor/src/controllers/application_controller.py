"""The central application controller for the Model-View-Controller architecture"""

from pse.umlsl_editor.src.commands.add_car import AddCarCommand
from pse.umlsl_editor.src.core.dataclasses.params import CarParams


class ApplicationController:
    def __init__(self):
        pass

    def add_car(self, **car_params: CarParams) -> bool:
        """
        Adds a car to the traffic snapshot.

        Args:
            **car_params: Car creation parameters. See CarParams TypedDict for all available parameters.
                         Required: name, assigned_road, lane_index, lane_direction
                         Optional: color, position_on_lane, transition, velocity, length, next_turn

        Returns:
            True if the car was successfully added, False otherwise.
        """
        # create the AddCarCommand, execute it and return the result
        pass