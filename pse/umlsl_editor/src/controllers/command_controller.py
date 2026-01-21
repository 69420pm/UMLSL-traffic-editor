"""Controller responsible for executing commands that modify the model."""

from typing import Optional

from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.entities.car import CarParams
from pse.umlsl_editor.src.model.entities.road import Road, LaneDirection
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.commands.cars import add_car
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane


class CommandController:
    """
    Manages command execution, validation.
    Provides high-level API for modifying the traffic snapshot.
    """

    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader, traffic_snapshot_writer: TrafficSnapshotWriter):
        """
        Initialize the command controller.

        Args:
            traffic_snapshot_reader: The model that will be modified by commands.
        """
        self.traffic_snapshot_reader = traffic_snapshot_reader
        self.traffic_snapshot_writer = traffic_snapshot_writer
        # self._command_history = []  # TODO: Implement undo/redo stack
        # self._history_position = -1  # Current position in history

    def execute_command(self, command: Command) -> None:
        """
        Executes a command with validation and potentially later adds it to the undo/redo history.

        Args:
            command: The command to execute.

        Returns:
            The return value from the command's execute() method.

        Raises:
            CommandValidationError: If the command fails validation.
        """
        raise NotImplementedError("Method not implemented yet.")

    def execute_without_history(self, command: Command) -> None:
        """
        Executes a command without adding it to the undo/redo history.
        Useful for ephemeral operations like selection changes.

        Args:
            command: The command to execute.

        Returns:
            The return value from the command's execute() method.

        Raises:
            CommandValidationError: If the command fails validation.
        """
        raise NotImplementedError("Method not implemented yet.")

    # def undo(self) -> bool:
    #     """
    #     Undoes the last command in the history.
    #
    #     Returns:
    #         True if undo was successful, False if there's nothing to undo.
    #     """
    #     raise NotImplementedError("Method not implemented yet.")
    #
    # def redo(self) -> bool:
    #     """
    #     Redoes the next command in the history.
    #
    #     Returns:
    #         True if redo was successful, False if there's nothing to redo.
    #     """
    #     raise NotImplementedError("Method not implemented yet.")
    #
    # def can_undo(self) -> bool:
    #     """Returns True if there are commands to undo."""
    #     raise NotImplementedError("Method not implemented yet.")
    #
    # def can_redo(self) -> bool:
    #     """Returns True if there are commands to redo."""
    #     raise NotImplementedError("Method not implemented yet.")
    #
    # High-level command API methods

    def add_car(
        self,
        name: str,
        assigned_road: Road,
        lane_index: int,
        lane_direction: LaneDirection,
        color: str,
        position_on_lane: float,
        transition: float,
        velocity: float,
        length: float,
        next_turn: Optional[TurnIntent]
    ) -> bool:
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
        acceleration : float = 1
        lane = Lane(assigned_road.name, lane_index, lane_direction)
        car_params = CarParams(name, lane, color, position_on_lane, transition, velocity, length, next_turn, acceleration)
        add_car_command = add_car.AddCarCommand(self.traffic_snapshot_reader, self.traffic_snapshot_writer, car_params)
        add_car_command.execute()
        raise NotImplementedError("Prototype Method")

    def remove_car(self, car_name: str) -> bool:
        """
        Removes a car from the traffic snapshot.

        Args:
            car_name: The unique identifier of the car to remove.

        Returns:
            True if the car was successfully removed, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")

    def edit_car(
        self,
        car_name: str,
        assigned_road: Optional[Road] = None,
        lane_index: Optional[int] = None,
        lane_direction: Optional[LaneDirection] = None,
        color: Optional[str] = None,
        position_on_lane: Optional[float] = None,
        transition: Optional[float] = None,
        velocity: Optional[float] = None,
        length: Optional[float] = None,
        next_turn: Optional[TurnIntent] = None
    ) -> bool:
        """
        Edits properties of an existing car.

        Args:
            car_name: The unique identifier of the car to edit.
            assigned_road: New road assignment (if provided).
            lane_index: New lane index (if provided).
            lane_direction: New lane direction (if provided).
            color: New color (if provided).
            position_on_lane: New position (if provided).
            transition: New transition value (if provided).
            velocity: New velocity (if provided).
            length: New length (if provided).
            next_turn: New turn intent (if provided).

        Returns:
            True if the car was successfully edited, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")

    def add_road(
        self,
        name: str,
        position: float,
        orientation: str,
        forward_lanes: int,
        backward_lanes: int
    ) -> bool:
        """
        Adds a road to the traffic snapshot.

        Args:
            name: Unique identifier for the road.
            position: Position coordinate (Y for horizontal, X for vertical).
            orientation: 'horizontal' or 'vertical'.
            forward_lanes: Number of lanes in forward direction.
            backward_lanes: Number of lanes in backward direction.

        Returns:
            True if the road was successfully added, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")

    def remove_road(self, road_name: str) -> bool:
        """
        Removes a road from the traffic snapshot.

        Args:
            road_name: The unique identifier of the road to remove.

        Returns:
            True if the road was successfully removed, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")

    def edit_road(
        self,
        road_name: str,
        position: Optional[float] = None,
        orientation: Optional[str] = None,
        forward_lanes: Optional[int] = None,
        backward_lanes: Optional[int] = None
    ) -> bool:
        """
        Edits properties of an existing road.

        Args:
            road_name: The unique identifier of the road to edit.
            position: New position (if provided).
            orientation: New orientation (if provided).
            forward_lanes: New forward lane count (if provided).
            backward_lanes: New backward lane count (if provided).

        Returns:
            True if the road was successfully edited, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")

    def add_umlsl_query(
        self,
        assigned_car_name: str,
        latex: str
    ) -> bool:
        """
        Adds a UMLSL query associated with a car.

        Args:
            assigned_car_name: The car this query is assigned to.
            latex: The LaTeX representation of the query.

        Returns:
            True if the query was successfully added, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")

    def remove_umlsl_query(self, query_id: str) -> bool:
        """
        Removes a UMLSL query.

        Args:
            query_id: The unique identifier of the query to remove.

        Returns:
            True if the query was successfully removed, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")

    def edit_umlsl_query(
        self,
        query_id: str,
        assigned_car_name: Optional[str] = None,
        latex: Optional[str] = None
    ) -> bool:
        """
        Edits an existing UMLSL query.

        Args:
            query_id: The unique identifier of the query to edit.
            assigned_car_name: New assigned car (if provided).
            latex: New LaTeX representation (if provided).

        Returns:
            True if the query was successfully edited, False otherwise.
        """
        raise NotImplementedError("Method not implemented yet.")


    def select_car(self, car_name: str) -> None:
        """
        Selects a car by its name.

        Args:
            car_name: The unique identifier of the car to select.
        """
        raise NotImplementedError("Method not implemented yet.")

    def deselect_car(self, car_name: str) -> None:
        """
        Deselects a car by its name.

        Args:
            car_name: The unique identifier of the car to deselect.
        """
        raise NotImplementedError("Method not implemented yet.")

    def select_road(self, road_name: str) -> None:
        """
        Selects a road by its name.

        Args:
            road_name: The unique identifier of the road to select.
        """
        raise NotImplementedError("Method not implemented yet.")

    def deselect_road(self, road_name: str) -> None:
        """
        Deselects a road by its name.

        Args:
            road_name: The unique identifier of the road to deselect.
        """
        raise NotImplementedError("Method not implemented yet.")

    def clear_selection(self) -> None:
        """
        Clears the selection of all cars and roads.
        """
        raise NotImplementedError("Method not implemented yet.")

    # todo correct skeletons for load/save traffic snapshot
    def load_traffic_snapshot(self) -> None:
        """
        """
        raise NotImplementedError("Method not implemented yet.")

    def save_traffic_snapshot(self) -> None:
        """
        """
        raise NotImplementedError("Method not implemented yet.")
    def save_as_traffic_snapshot(self) -> None:
        """
        """
        raise NotImplementedError("Method not implemented yet.")
    def change_breaking_acceleration(self, value: int) -> None :
        """
        Changes the breaking acceleration of the cars.
        """
        raise NotImplementedError("Method not implemented yet.")
    def toggle_coordinate_system(self) -> None:
        """
        Toggles weather the coordinate system in the visual editor should be rendered.
        """
        raise NotImplementedError("Method not implemented yet.")
    def toggle_safety_distance(self) -> None:
        """
        Toggles weather the safety distance of the cars in the visual editor should be rendered.
        """
        raise NotImplementedError("Method not implemented yet.")