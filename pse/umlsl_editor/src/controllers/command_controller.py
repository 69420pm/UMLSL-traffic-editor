"""Controller responsible for executing commands that modify the model."""

from typing import Optional

from pse.umlsl_editor.src.commands.cars import add_car
from pse.umlsl_editor.src.commands.cars.delete_car import DeleteCar
from pse.umlsl_editor.src.commands.cars.edit_car import EditCarCommand
from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.commands.roads import add_road
from pse.umlsl_editor.src.commands.roads import delete_road
from pse.umlsl_editor.src.commands.roads import edit_road
from pse.umlsl_editor.src.commands.selection.clear_selection import ClearSelection
from pse.umlsl_editor.src.commands.umlsl import add_umlsl_query
from pse.umlsl_editor.src.commands.umlsl import delete_umlsl_query
from pse.umlsl_editor.src.commands.umlsl import edit_umlsl_query
from pse.umlsl_editor.src.commands.selection.select_entity import SelectEntity
from pse.umlsl_editor.src.commands.settings.change_breaking_acceleration import ChangeBreakingAccelerationCommand
from pse.umlsl_editor.src.commands.settings.set_coordinate_system import SetCoordinateSystemCommand
from pse.umlsl_editor.src.commands.settings.set_safety_distance import SetSafetyDistanceCommand
from pse.umlsl_editor.src.model.domain_models.selection_model import SelectionModel
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel
from pse.umlsl_editor.src.model.entities.car import CarParams, Car
from pse.umlsl_editor.src.model.entities.road import Road, RoadParams, RoadOrientation
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery, UMLSLQueryParams
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent


class CommandController:
    """
    Manages command execution, validation.
    Provides high-level API for modifying the traffic snapshot.
    """

    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader, traffic_snapshot_writer: TrafficSnapshotWriter,
                 umlsl_queries_model: UMLSLQueriesModel, settings_model: SettingsModel,
                 selection_model: SelectionModel):
        """
        Initialize the command controller.

        Args:
            traffic_snapshot_reader: The model that will be modified by commands.
        """
        self.traffic_snapshot_reader = traffic_snapshot_reader
        self.traffic_snapshot_writer = traffic_snapshot_writer
        self.umlsl_queries_model = umlsl_queries_model
        self.settings_model = settings_model
        self.selection_model = selection_model
        # self._command_history = []  # TODO: Implement undo/redo stack
        # self._history_position = -1  # Current position in history

    def _execute_command(self, command: Command) -> None:
        """
        Executes a command with validation and potentially later adds it to the undo/redo history.

        Args:
            command: The command to execute.

        Returns:
            The return value from the command's execute() method.

        Raises:
            CommandValidationError: If the command fails validation.
        """
        command.execute()

    def _execute_without_history(self, command: Command) -> None:
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
        command.execute()

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
            color: str,
            position_on_lane: float,
            transition: float,
            velocity: float,
            length: float,
            acceleration: float,
            next_turn: Optional[TurnIntent]
    ) -> None:
        """
        Adds a car to the traffic snapshot based on the given parameters.

        Args:
            name: Unique human-readable identifier for the car.
            assigned_road: Reference to the Road the car is currently traveling on.
            lane_index: Index of the lane the car is currently in.
            color: Hex color code
            position_on_lane: Distance along lane
            transition: Lane change progress
            velocity: Current speed
            length: Physical length
            acceleration: Current acceleration
            next_turn: Turn intent at intersection

        """
        lane = Lane(road_uid=assigned_road.uid, lane_index=lane_index)
        car_params = CarParams(name, lane, color, position_on_lane, transition, velocity, length, next_turn,
                               acceleration)
        add_car_command = add_car.AddCarCommand(self.traffic_snapshot_reader, self.traffic_snapshot_writer, car_params)
        self._execute_command(add_car_command)

    def remove_car(self, car_uid: str) -> None:
        """
        Removes a car from the traffic snapshot.

        Args:
            car_uid: The unique identifier of the car to remove.

        """
        remove_car_command = DeleteCar(self.traffic_snapshot_writer, self.traffic_snapshot_reader, car_uid)
        self._execute_command(remove_car_command)

    _UNCHANGED = object()

    def edit_car(
            self,
            car: Car,
            car_name: object = _UNCHANGED,
            road_uid: object = _UNCHANGED,
            lane_index: object = _UNCHANGED,
            color: object = _UNCHANGED,
            position_on_lane: object = _UNCHANGED,
            transition: object = _UNCHANGED,
            velocity: object = _UNCHANGED,
            length: object = _UNCHANGED,
            next_turn: object = _UNCHANGED,
            acceleration: object = _UNCHANGED,
    ) -> None:
        """
        Edits properties of an existing car using a merge strategy:
        any parameter left as _UNCHANGED keeps the current value.
        Passing next_turn=None explicitly clears it.
        """

        if road_uid is self._UNCHANGED and lane_index is self._UNCHANGED:
            lane = car.lane
        else:
            road_uid = car.lane.road_uid if road_uid is self._UNCHANGED else road_uid
            lane_index = car.lane.lane_index if lane_index is self._UNCHANGED else lane_index
            lane = Lane(road_uid=road_uid, lane_index=lane_index)

        car_params = CarParams(
            name=car.name if car_name is self._UNCHANGED else car_name,
            lane=lane,
            color=car.color if color is self._UNCHANGED else color,
            position_on_lane=car.position_on_lane if position_on_lane is self._UNCHANGED else position_on_lane,
            transition=car.transition if transition is self._UNCHANGED else transition,
            speed=car.speed if velocity is self._UNCHANGED else velocity,
            length=car.length if length is self._UNCHANGED else length,
            next_turn=car.next_turn if next_turn is self._UNCHANGED else next_turn,
            acceleration=car.acceleration if acceleration is self._UNCHANGED else acceleration,
        )

        edit_car_command = EditCarCommand(
            self.traffic_snapshot_reader,
            self.traffic_snapshot_writer,
            car_params,
            car.uid,
        )
        self._execute_command(edit_car_command)

    def add_road(
            self,
            name: str,
            orientation: RoadOrientation,
            position: float,
            number_of_forward_lanes: int,
            number_of_backward_lanes: int
    ) -> None:
        """
        Adds a road to the traffic snapshot based on the given parameters.

        Args:
            name: Unique human-readable identifier for the road.
            orientation: The orientation of the road (horizontal or vertical).
            position: The position of the road in the coordinate system.
            number_of_forward_lanes: Number of lanes in the forward direction.
            number_of_backward_lanes: Number of lanes in the backward direction.
        """
        road_params = RoadParams(name, orientation, position, number_of_forward_lanes, number_of_backward_lanes)
        add_road_command = add_road.AddRoadCommand(self.traffic_snapshot_reader, self.traffic_snapshot_writer,
                                                   road_params)
        self._execute_command(add_road_command)

    def remove_road(self, road_uid: str) -> None:
        """
        Removes a road from the traffic snapshot.

        Args:
            road_uid: The unique identifier of the road to remove.
        """
        remove_road_command = delete_road.DeleteRoad(self.traffic_snapshot_writer, self.traffic_snapshot_reader,
                                                     road_uid)
        self._execute_command(remove_road_command)

    def update_road(
            self,
            road: Road,
            name: object = _UNCHANGED,
            orientation: object = _UNCHANGED,
            position: object = _UNCHANGED,
            number_of_forward_lanes: object = _UNCHANGED,
            number_of_backward_lanes: object = _UNCHANGED
    ) -> None:
        """
        Updates an existing road using a merge strategy.
        """
        road_params = RoadParams(
            name=road.name if name is self._UNCHANGED else name,
            orientation=road.orientation if orientation is self._UNCHANGED else orientation,
            position=road.position if position is self._UNCHANGED else position,
            number_of_forward_lanes=road.number_of_forward_lanes if number_of_forward_lanes is self._UNCHANGED else number_of_forward_lanes,
            number_of_backward_lanes=road.number_of_backward_lanes if number_of_backward_lanes is self._UNCHANGED else number_of_backward_lanes
        )

        edit_road_command = edit_road.EditRoadCommand(
            self.traffic_snapshot_reader,
            self.traffic_snapshot_writer,
            road_params,
            road.uid
        )
        self._execute_command(edit_road_command)

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
        umlsl_query_params = UMLSLQueryParams(latex, assigned_car_name)
        add_umlsl_query_command = add_umlsl_query.AddUMLSLQuery(umlsl_query_params, self.umlsl_queries_model)
        self._execute_command(add_umlsl_query_command)

    def remove_umlsl_query(self, query_id: str) -> None:
        """
        Removes a UMLSL query.

        Args:
            query_id: The unique identifier of the query to remove.
        """
        remove_umlsl_query_command = delete_umlsl_query.DeleteUMLSLQuery(query_id, self.umlsl_queries_model)
        self._execute_command(remove_umlsl_query_command)

    def update_umlsl_query(
            self,
            query: UMLSLQuery,
            assigned_car_name: object = _UNCHANGED,
            latex: object = _UNCHANGED
    ) -> None:
        """
        Edits an existing UMLSL query using a merge strategy.

        Args:
            query: The query object to edit.
            assigned_car_name: New assigned car name (optional).
            latex: New LaTeX string (optional).
        """
        umlsl_query_params = UMLSLQueryParams(
            latex=query.latex if latex is self._UNCHANGED else latex,
            assigned_car_uid=query.assigned_car_name if assigned_car_name is self._UNCHANGED else assigned_car_name
        )
        edit_umlsl_query_command = edit_umlsl_query.EditUMLSLQuery(query.uid, umlsl_query_params,
                                                                   self.umlsl_queries_model)
        self._execute_command(edit_umlsl_query_command)

    def select_entity(self, uid: str) -> None:
        """
        Selects a car or road by its unique identifier.
        Args:
            uid: The unique identifier of the car or road to select.
        """
        SelectEntity(self.traffic_snapshot_writer, uid).execute()

    def clear_selection(self) -> None:
        """
        Clears the selection of all cars and roads.
        """
        ClearSelection(self.traffic_snapshot_writer).execute()

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

    def change_breaking_acceleration(self, value: float) -> None:
        """
        Changes the breaking acceleration of the cars.
        """
        change_breaking_acceleration_command = ChangeBreakingAccelerationCommand(self.settings_model, value)
        self._execute_command(change_breaking_acceleration_command)

    def set_coordinate_system(self, value: bool) -> None:
        """
        Toggles weather the coordinate system in the visual editor should be rendered.
        """
        toggle_coordinate_system_command = SetCoordinateSystemCommand(self.settings_model, value)
        self._execute_command(toggle_coordinate_system_command)

    def toggle_safety_distance(self, value: bool) -> None:
        """
        Toggles weather the safety distance of the cars in the visual editor should be rendered.
        """
        toggle_safety_distance_command = SetSafetyDistanceCommand(self.settings_model, value)
        self._execute_command(toggle_safety_distance_command)
