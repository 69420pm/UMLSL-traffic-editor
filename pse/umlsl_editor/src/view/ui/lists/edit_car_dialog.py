"""
Car editing dialog for the UMLSL Traffic Editor.

Provides a dialog for creating new cars or editing existing car properties
such as name, color, speed, lane assignment, and turn direction.
"""
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QSignalBlocker, QTimer
from PySide6.QtWidgets import QDialog, QWidget

from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.errors.car_errors import (
    CarTrafficSnapshotContextValidationError,
    CarValidationError,
)
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import (
    TurnDirection,
    TurnIntent,
)
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog
from pse.umlsl_editor.src.view.ui.lists.confirm_deletion_dialog import (
    ConfirmDeletionDialog,
)
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_car_dialog import (
    Ui_Edit_Car_Dialog,
)

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

# Default values for new cars
DEFAULT_CAR_CONFIG = {
    "color": "lightblue",
    "length": 1,
    "speed": 0.0,
    "acceleration": 0.0,
    "position": 0.0,
    "transition": 0.0,
}


class EditCarDialog(QDialog, Ui_Edit_Car_Dialog):
    """
    Dialog for creating or editing car entities.
    """

    def __init__(
            self,
            car: Car | None,
            application_controller: "ApplicationController",
            parent: QWidget | None = None,
    ) -> None:
        """
        Initialize the car editing dialog.

        Args:
            car: The car to edit, or None to create a new car.
            application_controller: The application controller for executing commands.
            parent: The parent widget for this dialog.
        """
        super().__init__(parent)
        self.setupUi(self)

        self._app_controller = application_controller
        self._road_dict = self._app_controller.data_controller.get_all_roads()
        self._roads_list = list(self._road_dict.values())

        # Validate environment state immediately
        self._can_open = bool(self._roads_list)
        if not self._can_open:
            return

        self.is_edit_mode = car is not None
        self.car = car if car else self._create_default_car()

        self._init_ui()

    def exec(self) -> int:
        """
        Execute the dialog.
        Checks if the environment is valid (roads exist) before showing.
        """
        if not self._can_open:
            # Postpone warning to allow the event loop to process it properly
            QTimer.singleShot(0, self._show_no_roads_warning)
            return QDialog.DialogCode.Rejected
        return super().exec()

    # =========================================================================
    # Initialization & Setup
    # =========================================================================

    def _init_ui(self) -> None:
        """Initialize UI state and connections."""
        self._populate_basic_fields()
        self._populate_road_selector()
        self._populate_turn_fields()
        self._connect_signals()

    def _create_default_car(self) -> Car:
        """Create a transient Car entity with default parameters for the form."""
        first_road = self._roads_list[0]
        # Prefer forward lanes, fallback to backward
        default_lane = (
            first_road.forward_lanes[0]
            if first_road.forward_lanes
            else first_road.backward_lanes[0]
        )

        params = CarParams(
            name="default",
            color=DEFAULT_CAR_CONFIG["color"],
            length=DEFAULT_CAR_CONFIG["length"],
            speed=DEFAULT_CAR_CONFIG["speed"],
            acceleration=DEFAULT_CAR_CONFIG["acceleration"],
            position_on_lane=DEFAULT_CAR_CONFIG["position"],
            transition=DEFAULT_CAR_CONFIG["transition"],
            next_turn=None,
            lane=default_lane,
            braking_distance=self._app_controller.get_braking_distance()
        )

        snapshot_reader = self._app_controller.get_traffic_snapshot_reader()
        return Car.from_params(params, snapshot_reader)

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        self.b_save.clicked.connect(self._on_save_clicked)
        self.b_delete.clicked.connect(self._on_delete_clicked)
        self.d_road.currentIndexChanged.connect(self._on_road_changed)
        self.d_direction.currentIndexChanged.connect(self._on_direction_changed)

    # =========================================================================
    # Form Population (View Logic)
    # =========================================================================

    def _populate_basic_fields(self) -> None:
        """Populate non-relational fields (Strings, Numbers)."""
        self.t_name.setText(self.car.name)
        self.t_color.setText(self.car.color)
        self.s_length.setValue(self.car.length)
        self.s_speed.setValue(self.car.speed)
        self.s_acceleration.setValue(self.car.acceleration)
        self.s_position.setValue(self.car.position_on_lane)
        self.s_transition.setValue(self.car.transition)

    def _populate_road_selector(self) -> None:
        """Initialize road dropdown and trigger lane population."""
        self.d_road.blockSignals(True)
        self.d_road.clear()
        self.d_road.addItems([road.name for road in self._roads_list])

        # Find and select the car's current road
        current_road = self._road_dict.get(self.car.lane.road_uid)
        if current_road:
            index = self._roads_list.index(current_road)
            self.d_road.setCurrentIndex(index)
            self._update_lane_dropdown(current_road, self.car.lane.lane_index)

        self.d_road.blockSignals(False)

    def _populate_turn_fields(self) -> None:
        """Populate turn direction and visibility."""
        directions = [d.name for d in TurnDirection]

        # Determine current direction state
        has_turn = self.car.next_turn is not None
        current_dir = self.car.next_turn.direction if has_turn else TurnDirection.STRAIGHT

        self.d_direction.clear()
        self.d_direction.addItems(directions)
        self.d_direction.setCurrentIndex(current_dir.value)

        self._toggle_turn_fields_visibility(is_straight=(current_dir == TurnDirection.STRAIGHT))

    def _update_lane_dropdown(self, road: "Road", target_lane_index: int | None) -> None:
        """
        Refresh lane dropdown based on the selected road.

        Args:
            road: The road entity to generate lanes from.
            target_lane_uid: If provided, tries to select this lane. Otherwise, defaults to 0.
        """
        # Combine backward and forward lanes into a flat list for the UI
        all_lanes = road.backward_lanes + road.forward_lanes
        lane_labels = [lane.get_name() for lane in all_lanes]

        with QSignalBlocker(self.d_lane):
            self.d_lane.clear()
            self.d_lane.addItems(lane_labels)

            selected_index = 0
            if target_lane_index is not None:
                selected_index = target_lane_index + road.number_of_backward_lanes

            print(selected_index)
            print(target_lane_index)
            print(road.number_of_backward_lanes)

            self.d_lane.setCurrentIndex(selected_index)

    def _toggle_turn_fields_visibility(self, is_straight: bool) -> None:
        """Show/Hide turn widgets based on direction."""
        widgets = [self.d_road_turn, self.l_road_turn, self.d_lane_turn, self.l_lane_turn]
        for widget in widgets:
            widget.setVisible(not is_straight)

    # =========================================================================
    # Signal Handlers (Controller Logic)
    # =========================================================================

    def _on_road_changed(self, index: int) -> None:
        """Handle user changing the road dropdown."""
        if index < 0:
            return

        selected_road = self._roads_list[index]
        # When user manually changes road, default to first lane (index 0)
        self._update_lane_dropdown(selected_road, target_lane_index=None)

    def _on_direction_changed(self, index: int) -> None:
        """Handle user changing turn direction."""
        is_straight = (index == TurnDirection.STRAIGHT.value)
        self._toggle_turn_fields_visibility(is_straight)

    def _on_save_clicked(self) -> None:
        """Validate input and execute save command."""
        try:
            form_data = self._collect_form_data()

            if self.is_edit_mode:
                self._execute_edit_command(form_data)
            else:
                self._execute_create_command(form_data)

            self.accept()

        except (CarValidationError, CarTrafficSnapshotContextValidationError) as e:
            WarningDialog("Validation Error", str(e), self).exec()

    def _on_delete_clicked(self) -> None:
        """Handle delete action for existing cars."""
        if not self.is_edit_mode:
            return

        # Confirm deletion with the user
        confirm = ConfirmDeletionDialog(
            f"Are you sure you want to delete the car '{self.car.name}'?",
            self,
        ).exec()

        if confirm == 1:
            # Defer deletion to next event loop iteration to allow QML signal
            # handlers to complete before the underlying data is destroyed.
            car_uid = self.car.uid
            QTimer.singleShot(0, lambda: self._app_controller.command_controller.remove_car(car_uid))
            self.accept()

    def _show_no_roads_warning(self) -> None:
        """Show warning for invalid environment."""
        WarningDialog(
            "Road Required",
            "Cars must be placed on a road.\nPlease add a road to your scene first.",
            self.parent(),
        ).exec()

    # =========================================================================
    # Data Processing
    # =========================================================================

    def _collect_form_data(self) -> dict[str, Any]:
        """Extract all data from UI widgets."""
        road_idx = self.d_road.currentIndex()
        road = self._roads_list[road_idx]

        # Calculate internal lane index (adjusting for backward/forward split)
        # Note: UI list is [backward..., forward...]
        # Internal model expects 0-based index relative to direction group?
        # Preserving original logic: `ui_index - num_backward`
        lane_relative_index = self.d_lane.currentIndex() - road.number_of_backward_lanes

        # Construct Turn Intent
        turn_dir = TurnDirection(self.d_direction.currentIndex())
        # TODO: 'turn_lane' currently uses a placeholder logic.
        # Update this if specific target lane selection for turns is implemented in UI.
        turn_target = Lane(lane_index=0, road_uid="")
        turn_intent = TurnIntent(direction=turn_dir, target_lane=turn_target)

        return {
            "name": self.t_name.text(),
            "color": self.t_color.text(),
            "length": self.s_length.value(),
            "speed": self.s_speed.value(),
            "acceleration": self.s_acceleration.value(),
            "position": self.s_position.value(),
            "transition": self.s_transition.value(),
            "road": road,
            "lane_index": lane_relative_index,
            "next_turn": turn_intent,
        }

    def _execute_edit_command(self, data: dict) -> None:
        self._app_controller.command_controller.edit_car(
            car=self.car,
            car_name=data["name"],
            color=data["color"],
            length=data["length"],
            speed=data["speed"],
            acceleration=data["acceleration"],
            position_on_lane=data["position"],
            transition=data["transition"],
            road_uid=data["road"].uid,
            lane_index=data["lane_index"],
            next_turn=data["next_turn"],
        )

    def _execute_create_command(self, data: dict) -> None:
        self._app_controller.command_controller.add_car(
            name=data["name"],
            color=data["color"],
            length=data["length"],
            speed=data["speed"],
            acceleration=data["acceleration"],
            position_on_lane=data["position"],
            transition=data["transition"],
            assigned_road=data["road"],
            lane_index=data["lane_index"],
            next_turn=data["next_turn"],
            braking_distance=self._app_controller.get_braking_distance()
        )
