"""The central application controller for the Model-View-Controller architecture"""
from typing import Any, Optional

from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.core.dataclasses.road import Road, LaneDirection
from pse.umlsl_editor.src.core.dataclasses.turn_intent import TurnIntent
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.view.main_window import MainWindow


class ApplicationController:
    def __init__(self, traffic_snapshot: TrafficSnapshot, main_window: MainWindow):
        self.traffic_snapshot = traffic_snapshot
        self.main_window = main_window
        self._setup_event_listeners()

    def _setup_event_listeners(self) -> None:
        """
        Connects TrafficSnapshot signals to View slots.
        """
        # Connect Model signals to Controller handlers (or directly to View slots)
        self.traffic_snapshot.car_added.connect(self._on_car_added)
        self.traffic_snapshot.car_removed.connect(self._on_car_removed)
        self.traffic_snapshot.car_updated.connect(self._on_car_updated)

        self.traffic_snapshot.road_added.connect(self._on_road_added)
        self.traffic_snapshot.road_removed.connect(self._on_road_removed)
        self.traffic_snapshot.road_updated.connect(self._on_road_updated)

    def _on_car_added(self, car_data: Any) -> None:
        """
        Callback for when a car is added to the model.
        Delegates to the scene to create a visual representation.
        """
        self.main_window.get_scene().add_car_item(car_data)

    def _on_car_removed(self, car_data: Any) -> None:
        """
        Callback for when a car is removed from the model.
        Delegates to the scene to remove the visual representation.
        """
        self.main_window.get_scene().remove_car_item(car_data)

    def _on_car_updated(self, car_data: Any) -> None:
        """
        Callback for when a car is updated in the model.
        Delegates to the scene to update the visual representation.
        """
        self.main_window.get_scene().update_car_item(car_data)

    def _on_road_added(self, road_data: Any) -> None:
        """
        Callback for when a road is added to the model.
        Delegates to the scene to create a visual representation.
        """
        self.main_window.get_scene().add_road_item(road_data)

    def _on_road_removed(self, road_data: Any) -> None:
        """
        Callback for when a road is removed from the model.
        Delegates to the scene to remove the visual representation.
        """
        self.main_window.get_scene().remove_road_item(road_data)

    def _on_road_updated(self, road_data: Any) -> None:
        """
        Callback for when a road is updated in the model.
        Delegates to the scene to update the visual representation.
        """
        self.main_window.get_scene().update_road_item(road_data)

    def _execute_command(self, command: Command):
        """Executes the given command after validating it."""
        raise NotImplementedError()

    def add_car(
        self,
        name: str,
        assigned_road: Road,
        lane_index: int,
        lane_direction: LaneDirection,
        color:  str,
        position_on_lane: float,
        transition: float,
        velocity: float,
        length: float,
        next_turn: Optional[TurnIntent]) -> bool:
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
        # create the AddCarCommand, validate it, execute it and return the result
        raise NotImplementedError("Method not implemented yet.")
