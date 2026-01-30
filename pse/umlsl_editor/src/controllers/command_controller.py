"""Controller responsible for executing commands that modify the model."""

from typing import Optional

from pse.umlsl_editor.src.commands.cars.delete_car import DeleteCar
from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.commands.roads.add_road import AddRoad
from pse.umlsl_editor.src.commands.roads.delete_road import DeleteRoad
from pse.umlsl_editor.src.commands.roads.edit_road import EditRoad
from pse.umlsl_editor.src.commands.settings.change_breaking_acceleration import ChangeBreakingAccelerationCommand
from pse.umlsl_editor.src.commands.settings.toggle_coordinate_system import ToggleCoordinateSystemCommand
from pse.umlsl_editor.src.commands.settings.toggle_safety_distance import ToggleSafetyDistanceCommand
from pse.umlsl_editor.src.commands.umlsl.add_umlsl_query import AddUMLSLQuery
from pse.umlsl_editor.src.commands.umlsl.delete_umlsl_query import DeleteUMLSLQuery
from pse.umlsl_editor.src.commands.umlsl.edit_umlsl_query import EditUMLSLQuery
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel
from pse.umlsl_editor.src.model.entities.car import CarParams
from pse.umlsl_editor.src.model.entities.road import Road, LaneDirection, RoadParams, RoadOrientation
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery, UMLSLQueryParams
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent
from pse.umlsl_editor.src.commands.cars import add_car, edit_car
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane


class CommandController:
    """
    Manages command execution, validation.
    Provides high-level API for modifying the traffic snapshot.
    """

    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader, traffic_snapshot_writer: TrafficSnapshotWriter, umlsl_queries_model: UMLSLQueriesModel, settings_model : SettingsModel):
        """
        Initialize the command controller.

        Args:
            traffic_snapshot_reader: The model that will be modified by commands.
        """
        self.traffic_snapshot_reader = traffic_snapshot_reader
        self.traffic_snapshot_writer = traffic_snapshot_writer
        self.umlsl_queries_model = umlsl_queries_model
        self.settings_model = settings_model
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
    ) -> None:
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

        """
        #TODO: Change acceleration variable to actual acceleration
        acceleration : float = 1
        lane = Lane(road_uid=assigned_road.uid , lane_index=lane_index, lane_direction= lane_direction)
        car_params = CarParams(name, lane, color, position_on_lane, transition, velocity, length, next_turn, acceleration)
        add_car_command = add_car.AddCarCommand(self.traffic_snapshot_reader, self.traffic_snapshot_writer, car_params)
        add_car_command.execute()
        raise NotImplementedError("Prototype Method")

    def remove_car(self, car_name: str) -> None:
        """
        Removes a car from the traffic snapshot.

        Args:
            car_name: The unique identifier of the car to remove.

        """
        remove_car_command = DeleteCar(self.traffic_snapshot_writer, self.traffic_snapshot_reader, car_name)
        remove_car_command.execute()
        raise NotImplementedError("Prototype Method")

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
    ) -> None:
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

        """
        acceleration: float = 1
        lane = Lane(road_uid=assigned_road.uid, lane_index=lane_index, lane_direction=lane_direction)
        car_params = CarParams(car_name, lane, color, position_on_lane, transition, velocity, length, next_turn,
                               acceleration)
        edit_car_command = edit_car.EditCarCommand(self.traffic_snapshot_reader, self.traffic_snapshot_writer, car_params)
        edit_car_command.execute()
        raise NotImplementedError("Prototype Method")

    def add_road(
        self,
        name: str,
        position: float,
        orientation: str,
        forward_lanes: int,
        backward_lanes: int
    ) -> None:
        """
        Adds a road to the traffic snapshot.

        Args:
            name: Unique identifier for the road.
            position: Position coordinate (Y for horizontal, X for vertical).
            orientation: 'horizontal' or 'vertical'.
            forward_lanes: Number of lanes in forward direction.
            backward_lanes: Number of lanes in backward direction.

        """
        #TODO: Cast string to actual road orientation, how does this work?
        road_orientation = RoadOrientation(orientation)
        road_params = RoadParams(name, road_orientation, position, forward_lanes, backward_lanes)
        add_road_command = AddRoad(self.traffic_snapshot_writer, self.traffic_snapshot_reader, road_params)
        add_road_command.execute()
        raise NotImplementedError("Prototype Method")

    def remove_road(self, road_name: str) -> None:
        """
        Removes a road from the traffic snapshot.

        Args:
            road_name: The unique identifier of the road to remove.

        """
        remove_road_command = DeleteRoad(self.traffic_snapshot_writer, self.traffic_snapshot_reader, road_name)
        remove_road_command.execute()
        raise NotImplementedError("Prototype Method")

    def edit_road(
        self,
        road_name: str,
        position: Optional[float] = None,
        orientation: Optional[str] = None,
        forward_lanes: Optional[int] = None,
        backward_lanes: Optional[int] = None
    ) -> None:
        """
        Edits properties of an existing road.

        Args:
            road_name: The unique identifier of the road to edit.
            position: New position (if provided).
            orientation: New orientation (if provided).
            forward_lanes: New forward lane count (if provided).
            backward_lanes: New backward lane count (if provided).

        """
        road_orientation = RoadOrientation(orientation)
        road_params = RoadParams(road_name, road_orientation, position, forward_lanes, backward_lanes)
        edit_road_command = EditRoad(self.traffic_snapshot_reader, self.traffic_snapshot_writer, road_params)
        edit_road_command.execute()
        raise NotImplementedError("Prototype Method")

    def add_umlsl_query(
        self,
        assigned_car_name: str,
        latex: str
    ) -> None:
        """
        Adds a UMLSL query associated with a car.

        Args:
            assigned_car_name: The car this query is assigned to.
            latex: The LaTeX representation of the query.

        """
        #TODO: Add real validation parameter
        validation: bool = True
        umlsl_query_params = UMLSLQueryParams(latex, assigned_car_name, validation)
        add_umlsl_query = AddUMLSLQuery(umlsl_query_params, self.umlsl_queries_model)
        add_umlsl_query.execute()
        raise NotImplementedError("Prototype Method")

    def remove_umlsl_query(self, query_id: str) -> None:
        """
        Removes a UMLSL query.

        Args:
            query_id: The unique identifier of the query to remove.

        """
        remove_umlsl_query_command = DeleteUMLSLQuery(query_id, self.umlsl_queries_model)
        remove_umlsl_query_command.execute()
        raise NotImplementedError("Prototype Method")

    def edit_umlsl_query(
        self,
        query_id: str,
        assigned_car_name: Optional[str] = None,
        latex: Optional[str] = None
    ) -> None:
        """
        Edits an existing UMLSL query.

        Args:
            query_id: The unique identifier of the query to edit.
            assigned_car_name: New assigned car (if provided).
            latex: New LaTeX representation (if provided).

        """
        # TODO: Add real validation parameter
        validation: bool = True
        umlsl_query_params = UMLSLQueryParams(latex, assigned_car_name, validation)
        edit_umlsl_query = EditUMLSLQuery(query_id, umlsl_query_params, self.umlsl_queries_model)
        edit_umlsl_query.execute()
        raise NotImplementedError("Prototype Method")


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
        change_breaking_acceleration_command = ChangeBreakingAccelerationCommand(self.settings_model, value)
        change_breaking_acceleration_command.execute()
        raise NotImplementedError("Prototype Method")

    def toggle_coordinate_system(self) -> None:
        """
        Toggles weather the coordinate system in the visual editor should be rendered.
        """
        toggle_coordinate_system_command = ToggleCoordinateSystemCommand(self.settings_model)
        toggle_coordinate_system_command.execute()
        raise NotImplementedError("Prototype Method")

    def toggle_safety_distance(self) -> None:
        """
        Toggles weather the safety distance of the cars in the visual editor should be rendered.
        """
        toggle_safety_distance_command = ToggleSafetyDistanceCommand(self.settings_model)
        toggle_safety_distance_command.execute()
        raise NotImplementedError("Prototype Method")