"""
Car editing dialog for the UMLSL Traffic Editor.

Provides a dialog for creating new cars or editing existing car properties
such as name, color, speed, lane assignment, and turn direction.
"""
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QSignalBlocker, QTimer
from PySide6.QtWidgets import QDialog, QWidget

from pse.umlsl_editor.src.model.entities.car import Car
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
from pse.umlsl_editor.src.view.ui.lists.deletion_checks import (
    get_car_deletion_block_reason,
)
from pse.umlsl_editor.src.view.ui.lists.edit_dialogs.confirm_deletion_dialog import (
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
    "speed": 10.0,
    "acceleration": 1.0,
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
        self.car: Car | None = car if car else None

        # Cache for valid turn lanes to prevent excessive lookups
        self._current_valid_turn_lanes: list[Lane] = []

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
        self._connect_signals()

        # Populate turn fields last, as they depend on the connections and
        # values of the fields populated above.
        self._populate_turn_fields()

    def _get_default_lane(self) -> Lane:
        """Return a default lane for create mode."""
        first_road = self._roads_list[0]
        return (
            first_road.forward_lanes[0]
            if first_road.forward_lanes
            else first_road.backward_lanes[0]
        )

    def _get_default_car_values(self) -> dict[str, Any]:
        """Return default car field values for create mode."""
        return {
            "name": "default",
            "color": DEFAULT_CAR_CONFIG["color"],
            "length": DEFAULT_CAR_CONFIG["length"],
            "speed": DEFAULT_CAR_CONFIG["speed"],
            "acceleration": DEFAULT_CAR_CONFIG["acceleration"],
            "position": DEFAULT_CAR_CONFIG["position"],
            "transition": DEFAULT_CAR_CONFIG["transition"],
        }

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        self.b_save.clicked.connect(self._on_save_clicked)
        self.b_delete.clicked.connect(self._on_delete_clicked)

        # Structure changes
        self.d_road.currentIndexChanged.connect(self._on_road_changed)
        self.d_direction.currentIndexChanged.connect(self._on_direction_changed)

        # Triggers for updating valid turn lanes
        # The turn options depend on position, speed, length, lane and direction.
        # We connect all these inputs to the update handler.
        self.s_position.valueChanged.connect(self._update_turn_options)
        self.s_speed.valueChanged.connect(self._update_turn_options)
        self.s_length.valueChanged.connect(self._update_turn_options)
        self.d_lane.currentIndexChanged.connect(self._update_turn_options)
        # Note: d_direction and d_road also trigger this via their specific handlers

    # =========================================================================
    # Form Population (View Logic)
    # =========================================================================

    def _populate_basic_fields(self) -> None:
        """Populate non-relational fields (Strings, Numbers)."""
        if not self.is_edit_mode:
            self.setWindowTitle("Create New Car")
            self.b_delete.hide()
            defaults = self._get_default_car_values()
            self.t_name.setText(defaults["name"])
            self.t_color.setText(defaults["color"])
            self.s_length.setValue(defaults["length"])
            self.s_speed.setValue(defaults["speed"])
            self.s_acceleration.setValue(defaults["acceleration"])
            self.s_position.setValue(defaults["position"])
            self.s_transition.setValue(defaults["transition"])
            return

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

        if self.is_edit_mode and self.car is not None:
            current_road = self._road_dict.get(self.car.lane.road_uid)
            if current_road:
                index = self._roads_list.index(current_road)
                self.d_road.setCurrentIndex(index)
                self._update_lane_dropdown(current_road, self.car.lane.lane_index)
        else:
            default_road = self._roads_list[0]
            default_lane = self._get_default_lane()
            self.d_road.setCurrentIndex(0)
            self._update_lane_dropdown(default_road, default_lane.lane_index)

        self.d_road.blockSignals(False)

    def _populate_turn_fields(self) -> None:
        """Populate turn direction and visibility."""
        directions = [d.name for d in TurnDirection]

        # Determine current direction state
        has_turn = self.is_edit_mode and self.car is not None and self.car.next_turn is not None
        current_dir = self.car.next_turn.direction if has_turn else TurnDirection.STRAIGHT

        self.d_direction.blockSignals(True)
        self.d_direction.clear()
        self.d_direction.addItems(directions)
        self.d_direction.setCurrentIndex(current_dir.value)
        self.d_direction.blockSignals(False)

        # Force an update of the valid options based on the loaded car state
        self._update_turn_options()

        # If we have an existing turn, try to select the target lane in the dropdown
        if has_turn and current_dir != TurnDirection.STRAIGHT:
            self._select_turn_target_lane(self.car.next_turn.target_lane)

        self._toggle_turn_fields_visibility(is_straight=(current_dir == TurnDirection.STRAIGHT))

    def _update_lane_dropdown(self, road: "Road", target_lane_index: int | None) -> None:
        """
        Refresh lane dropdown based on the selected road.
        """
        all_lanes = road.backward_lanes + road.forward_lanes
        lane_labels = [lane.get_name() for lane in all_lanes]

        with QSignalBlocker(self.d_lane):
            self.d_lane.clear()
            self.d_lane.addItems(lane_labels)

            selected_index = 0
            if target_lane_index is not None:
                selected_index = target_lane_index + road.number_of_backward_lanes

            # Boundary check
            if selected_index < 0 or selected_index >= len(lane_labels):
                selected_index = 0

            self.d_lane.setCurrentIndex(selected_index)

    def _toggle_turn_fields_visibility(self, is_straight: bool) -> None:
        """Show/Hide turn widgets based on direction."""
        widgets = [self.d_road_turn, self.l_road_turn, self.d_lane_turn, self.l_lane_turn]
        for widget in widgets:
            widget.setVisible(not is_straight)

    def _select_turn_target_lane(self, target_lane: Lane) -> None:
        """Helper to select a specific lane object in the turn dropdown."""
        for i in range(self.d_lane_turn.count()):
            lane_data = self.d_lane_turn.itemData(i)
            if (lane_data and
                    lane_data.road_uid == target_lane.road_uid and
                    lane_data.lane_index == target_lane.lane_index):
                self.d_lane_turn.setCurrentIndex(i)
                return

    # =========================================================================
    # Signal Handlers (Controller Logic)
    # =========================================================================

    def _on_road_changed(self, index: int) -> None:
        """Handle user changing the road dropdown."""
        if index < 0:
            return

        selected_road = self._roads_list[index]
        # When user manually changes road, default to first lane (index 0 logic)
        self._update_lane_dropdown(selected_road, target_lane_index=None)

        # Road change affects position context, so update turn options
        self._update_turn_options()

    def _on_direction_changed(self, index: int) -> None:
        """Handle user changing turn direction."""
        is_straight = (index == TurnDirection.STRAIGHT.value)
        self._toggle_turn_fields_visibility(is_straight)

        # Direction is a key input for valid lanes
        self._update_turn_options()

    def _update_turn_options(self) -> None:
        """
        Dynamically update available turn target lanes based on current form values.
        """
        # 1. Check if update is needed (not needed for Straight)
        turn_dir = TurnDirection(self.d_direction.currentIndex())
        if turn_dir == TurnDirection.STRAIGHT:
            self.d_lane_turn.clear()
            self.d_road_turn.clear()
            return

        # 2. Reconstruct current Lane object from UI
        road_idx = self.d_road.currentIndex()
        if road_idx < 0: return
        current_road = self._roads_list[road_idx]

        ui_lane_idx = self.d_lane.currentIndex()
        # Map UI index back to internal signed/relative index
        relative_lane_index = ui_lane_idx - current_road.number_of_backward_lanes

        current_lane_obj = Lane(
            lane_index=relative_lane_index,
            road_uid=current_road.uid
        )

        # 3. Query Controller for valid lanes

        valid_lanes = self._app_controller.data_controller.get_valid_turn_intent_lanes(
            car_position=self.s_position.value(),
            car_speed=self.s_speed.value(),
            car_lane=current_lane_obj,
            car_length=self.s_length.value(),
            turn_direction=turn_dir
        )

        # 4. Update Dropdown
        # We block signals to prevent recursive triggers if we were to add logic there
        with QSignalBlocker(self.d_lane_turn):
            self.d_lane_turn.clear()

            if not valid_lanes:
                self.d_lane_turn.addItem("No valid lanes found")
                self.d_lane_turn.model().item(0).setEnabled(False)

            for lane in valid_lanes:
                # Format a readable label: "RoadName: Lane X"
                road_name = lane.road_uid
                if lane.road_uid in self._road_dict:
                    road_name = self._road_dict[lane.road_uid].name

                label = f"{road_name}: Lane {lane.lane_index}"

                # Store the actual Lane object in the item data for easy retrieval
                self.d_lane_turn.addItem(label, userData=lane)

            # Auto-select the first valid option if available
            if valid_lanes:
                self.d_lane_turn.setCurrentIndex(0)

        # Optional: If you want to populate d_road_turn as well (informational)
        # We can just display the unique road names found in valid_lanes
        unique_roads = {l.road_uid for l in valid_lanes}
        self.d_road_turn.clear()
        if len(unique_roads) == 0:
            self.d_road_turn.addItem("No valid road found")
            self.d_road_turn.model().item(0).setEnabled(False)
        self.d_road_turn.addItems([
            self._road_dict[uid].name if uid in self._road_dict else uid
            for uid in unique_roads
        ])

    def _on_save_clicked(self) -> None:
        """Validate input and execute save command."""
        try:
            form_data = self._collect_form_data()
            if not form_data:
                return

            if self.is_edit_mode:
                self._execute_edit_command(form_data)
            else:
                self._execute_create_command(form_data)


        except (CarValidationError, CarTrafficSnapshotContextValidationError) as e:
            WarningDialog("Validation Error", str(e), self).exec()
        else:
            self.parent().snackbar.show_message(
                f"Car '{form_data['name']}' " +
                ("updated successfully." if self.is_edit_mode else "created successfully."))
            self.accept()

    def _on_delete_clicked(self) -> None:
        """Handle delete action for existing cars."""
        if not self.is_edit_mode:
            return

        block_reason = get_car_deletion_block_reason(self._app_controller, self.car)
        if block_reason:
            WarningDialog("Deletion Error", block_reason, self).exec()
            return

        confirm = ConfirmDeletionDialog(
            f"Are you sure you want to delete the car '{self.car.name}'?",
            self,
        ).exec()

        if confirm == 1:
            car_uid = self.car.uid
            QTimer.singleShot(0, lambda: self._app_controller.command_controller.remove_car(car_uid))

            self.parent().snackbar.show_message(f"Car '{self.car.name}' deleted successfully.")
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

    def _collect_form_data(self) -> dict[str, Any] | None:
        """Extract all data from UI widgets."""
        road_idx = self.d_road.currentIndex()
        road = self._roads_list[road_idx]

        # Calculate internal lane index
        lane_relative_index = self.d_lane.currentIndex() - road.number_of_backward_lanes

        # Construct Turn Intent
        turn_dir = TurnDirection(self.d_direction.currentIndex())

        turn_intent = None
        if turn_dir == TurnDirection.STRAIGHT:
            # Usually Straight implies no specific target lane requirement in intent
            # or a specific 'Straight' intent. Assuming None represents 'Follow Road'.
            turn_intent = None
            # If your model requires an explicit TurnIntent for straight:
            # turn_intent = TurnIntent(direction=TurnDirection.STRAIGHT, target_lane=None)
        else:
            # Retrieve the selected Lane object from the dropdown's UserData
            selected_lane_data = self.d_lane_turn.currentData()

            if isinstance(selected_lane_data, Lane):
                turn_intent = TurnIntent(direction=turn_dir, target_lane=selected_lane_data)
            else:
                WarningDialog(
                    "No Valid Turn Lane",
                    "The car has no valid lanes to turn into based on its current position, speed and turning direction.\n",
                    self.parent(),
                ).exec()
                return None

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
            next_turn=data["next_turn"]
        )
