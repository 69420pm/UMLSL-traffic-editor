"""
Car editing dialog for the UMLSL Traffic Editor.

Provides a dialog for creating new cars or editing existing car properties
such as name, color, speed, lane assignment, and turn direction.
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_car_dialog import (
    Ui_Edit_Car_Dialog,
)


class EditCarDialog(QDialog, Ui_Edit_Car_Dialog):
    """
    Dialog for creating or editing car entities.

    This dialog provides form fields for all car properties including position,
    lane assignment, movement parameters, and turn intentions. It supports both
    creating new cars and editing existing ones.

    Attributes:
        car: The car entity being edited (or newly created).
        is_edit: True if editing an existing car, False if creating a new one.
        application_controller: Reference to the application controller for commands.
        road_dict: Dictionary of all available roads keyed by UID.
        roads_list: List of all available roads for indexing.
    """

    def __init__(
            self,
            car: Car | None,
            application_controller: "ApplicationController",
            parent=None,
    ) -> None:
        """
        Initialize the car editing dialog.

        Args:
            car: The car to edit, or None to create a new car.
            application_controller: The application controller for executing commands.
            parent: The parent widget for this dialog. Defaults to None.

        Raises:
            RuntimeError: If creating a new car when no roads exist.
        """
        super().__init__(parent)
        self.setupUi(self)

        self.car = car
        self.is_edit = car is not None
        self.application_controller = application_controller

        self.road_dict = application_controller.data_controller.get_all_roads()
        self.roads_list = list(self.road_dict.values())

        if not self.is_edit:
            self.car = self._create_default_car()

        self._populate_form_fields()
        self._connect_signals()

    def _create_default_car(self) -> Car:
        """
        Create a new car with default parameters.

        Returns:
            A new Car entity with default values.

        Raises:
            RuntimeError: If no roads are available for lane assignment.
        """
        if not self.road_dict:
            raise RuntimeError(
                "No roads available to assign default lane to the new car."
            )

        first_road = self.roads_list[0]
        default_lane = (
            first_road.forward_lanes[0]
            if first_road.forward_lanes
            else first_road.backward_lanes[0]
        )

        car_params = CarParams(
            name="",
            color="coral",
            length=1,
            speed=0.0,
            acceleration=0.0,
            position_on_lane=0.0,
            transition=0.0,
            next_turn=None,
            lane=default_lane,
        )
        return Car.from_params(car_params, self.application_controller.get_traffic_snapshot_reader())

    def _populate_form_fields(self) -> None:
        """Populate all form fields with the current car's values."""
        self._populate_basic_fields()
        self._populate_road_and_lane_fields()
        self._populate_turn_fields()

    def _populate_basic_fields(self) -> None:
        """Populate name, color, and movement parameter fields."""
        self.t_name.setText(self.car.name)
        self.t_color.setText(self.car.color)
        self.s_length.setValue(self.car.length)
        self.s_speed.setValue(self.car.speed)
        self.s_acceleration.setValue(self.car.acceleration)
        self.s_position.setValue(self.car.position_on_lane)
        self.s_transition.setValue(self.car.transition)

    def _populate_road_and_lane_fields(self) -> None:
        """Populate road and lane selection dropdowns."""
        current_road = self.road_dict[self.car.lane.road_uid]
        current_road_index = self.roads_list.index(current_road)

        self.d_road.addItems([road.name for road in self.road_dict.values()])
        self.d_road.setCurrentIndex(current_road_index)

        lane_labels = self._generate_lane_labels(current_road)
        self.d_lane.addItems(lane_labels)
        self.d_lane.setCurrentIndex(
            self.car.lane.lane_index + current_road.number_of_backward_lanes
        )

    def _generate_lane_labels(self, road) -> list[str]:
        """
        Generate lane labels for the lane dropdown.

        Args:
            road: The road entity to generate lane labels for.

        Returns:
            List of lane label strings (e.g., "Lane -1", "Lane 0", "Lane 1").
        """
        return [
            f"Lane {i}"
            for i in range(
                -road.number_of_backward_lanes, road.number_of_forward_lanes
            )
        ]

    def _populate_turn_fields(self) -> None:
        """Populate turn direction and related fields."""
        directions = [direction.value for direction in TurnDirection]
        car_drives_straight = (
                self.car.next_turn is None
                or self.car.next_turn.direction == TurnDirection.STRAIGHT
        )

        self.d_direction.clear()
        self.d_direction.addItems(directions)
        self.d_direction.setCurrentText(
            TurnDirection.STRAIGHT.value
            if car_drives_straight
            else self.car.next_turn.direction.value
        )

        if car_drives_straight:
            self._hide_turn_fields()
        else:
            self._show_turn_fields()

    def _hide_turn_fields(self) -> None:
        """Hide turn-related road and lane selection fields."""
        self.d_road_turn.hide()
        self.l_road_turn.hide()
        self.d_lane_turn.hide()
        self.l_lane_turn.hide()

    def _show_turn_fields(self) -> None:
        """Show turn-related road and lane selection fields."""
        self.d_road_turn.show()
        self.l_road_turn.show()
        self.d_lane_turn.show()
        self.l_lane_turn.show()

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        self.b_save.clicked.connect(self._save_and_close)

    def _save_and_close(self) -> None:
        """Save the car data and close the dialog."""
        car_data = self._collect_form_data()

        if self.is_edit:
            self._update_existing_car(car_data)
        else:
            self._create_new_car(car_data)

        self.accept()

    def _collect_form_data(self) -> dict:
        """
        Collect all form field values into a dictionary.

        Returns:
            Dictionary containing all car property values from the form.
        """
        road = self.roads_list[self.d_road.currentIndex()]
        lane_index = self.d_lane.currentIndex() - road.number_of_backward_lanes

        return {
            "name": self.t_name.text(),
            "color": self.t_color.text(),
            "length": self.s_length.value(),
            "speed": self.s_speed.value(),
            "acceleration": self.s_acceleration.value(),
            "position_on_lane": self.s_position.value(),
            "transition": self.s_transition.value(),
            "road": road,
            "lane_index": lane_index,
            "next_turn": None,
        }

    def _update_existing_car(self, data: dict) -> None:
        """
        Update an existing car with new values.

        Args:
            data: Dictionary of car properties to update.
        """
        self.application_controller.command_controller.edit_car(
            car=self.car,
            car_name=data["name"],
            color=data["color"],
            length=data["length"],
            speed=data["speed"],
            acceleration=data["acceleration"],
            position_on_lane=data["position_on_lane"],
            transition=data["transition"],
            road_uid=data["road"].uid,
            lane_index=data["lane_index"],
            next_turn=data["next_turn"],
        )

    def _create_new_car(self, data: dict) -> None:
        """
        Create a new car with the specified values.

        Args:
            data: Dictionary of car properties for the new car.
        """
        self.application_controller.command_controller.add_car(
            name=data["name"],
            color=data["color"],
            length=data["length"],
            speed=data["speed"],
            acceleration=data["acceleration"],
            position_on_lane=data["position_on_lane"],
            transition=data["transition"],
            assigned_road=data["road"],
            lane_index=data["lane_index"],
            next_turn=data["next_turn"],
        )
