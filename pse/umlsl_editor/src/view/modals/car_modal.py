"""
Modal dialog for creating and editing cars.
"""
from typing import Optional, Callable

from PySide6.QtWidgets import (
    QLineEdit, QDoubleSpinBox, QComboBox, QWidget, QPushButton, QColorDialog
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QColor

from pse.umlsl_editor.src.core.dataclasses.car import CarParams
from pse.umlsl_editor.src.core.dataclasses.road import Road, LaneDirection, Lane
from pse.umlsl_editor.src.core.dataclasses.turn_intent import TurnIntent
from pse.umlsl_editor.src.view.modals.entity_modal import EntityModal, ModalMode


class CarModal(EntityModal):
    """
    Modal dialog for creating or editing a car.

    Provides form fields for all car attributes and emits a CarParams
    object when the user confirms the dialog.
    """

    # Signal emitted when user confirms car creation/editing
    car_confirmed = Signal(CarParams)

    def __init__(
        self,
        mode: ModalMode = ModalMode.CREATE,
        get_roads: Optional[Callable[[], list[Road]]] = None,
        initial_data: Optional[dict] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the car modal.

        Args:
            mode: Operation mode (CREATE or EDIT).
            get_roads: Callback to retrieve available roads for dropdown.
            initial_data: Initial values for form fields (used in EDIT mode).
            parent: Parent widget.
        """
        # self.get_roads = get_roads or (lambda: [])
        # self.initial_data = initial_data or {}
        #
        # title = "Edit Car" if mode == ModalMode.EDIT else "Create Car"
        # super().__init__(title, mode, parent)
        #
        # # Populate initial data if in EDIT mode
        # if mode == ModalMode.EDIT and initial_data:
        #     self._populate_initial_data()

    def _setup_form(self) -> None:
        """Setup form fields for car attributes."""
        # # Name
        # self.name_input = QLineEdit()
        # self.form_layout.addRow("Name:", self.name_input)
        #
        # # Road selection
        # self.road_combo = QComboBox()
        # self._populate_roads()
        # self.form_layout.addRow("Road:", self.road_combo)
        #
        # # Lane index
        # self.lane_index_spin = QDoubleSpinBox()
        # self.lane_index_spin.setDecimals(0)
        # self.lane_index_spin.setMinimum(0)
        # self.lane_index_spin.setMaximum(10)
        # self.form_layout.addRow("Lane Index:", self.lane_index_spin)
        #
        # # Lane direction
        # self.lane_direction_combo = QComboBox()
        # self.lane_direction_combo.addItem("Forward", LaneDirection.FORWARD)
        # self.lane_direction_combo.addItem("Backward", LaneDirection.BACKWARD)
        # self.form_layout.addRow("Lane Direction:", self.lane_direction_combo)
        #
        # # Color
        # self.color_input = QLineEdit()
        # self.color_input.setPlaceholderText("#RRGGBB")
        # color_button = QPushButton("Choose Color")
        # color_button.clicked.connect(self._choose_color)
        # self.form_layout.addRow("Color:", self.color_input)
        # self.form_layout.addRow("", color_button)
        #
        # # Position on lane
        # self.position_spin = QDoubleSpinBox()
        # self.position_spin.setMinimum(0.0)
        # self.position_spin.setMaximum(10000.0)
        # self.position_spin.setDecimals(2)
        # self.form_layout.addRow("Position on Lane:", self.position_spin)
        #
        # # Transition
        # self.transition_spin = QDoubleSpinBox()
        # self.transition_spin.setMinimum(-0.99)
        # self.transition_spin.setMaximum(0.99)
        # self.transition_spin.setDecimals(2)
        # self.transition_spin.setSingleStep(0.1)
        # self.form_layout.addRow("Transition:", self.transition_spin)
        #
        # # Velocity
        # self.velocity_spin = QDoubleSpinBox()
        # self.velocity_spin.setMinimum(-100.0)
        # self.velocity_spin.setMaximum(100.0)
        # self.velocity_spin.setDecimals(2)
        # self.form_layout.addRow("Velocity:", self.velocity_spin)
        #
        # # Length
        # self.length_spin = QDoubleSpinBox()
        # self.length_spin.setMinimum(0.1)
        # self.length_spin.setMaximum(50.0)
        # self.length_spin.setDecimals(2)
        # self.length_spin.setValue(4.5)  # Default car length
        # self.form_layout.addRow("Length:", self.length_spin)
        #
        # # Next turn (optional, not implemented in detail)
        # # TODO: Add turn intent selection when TurnIntent structure is finalized

    def _populate_roads(self) -> None:
        """Populate road dropdown with available roads."""
        # self.road_combo.clear()
        # roads = self.get_roads()
        # for road in roads:
        #     self.road_combo.addItem(road.name, road)

    def _choose_color(self) -> None:
        """Open color picker dialog."""
        # current_color = QColor(self.color_input.text() or "#FF0000")
        # color = QColorDialog.getColor(current_color, self, "Choose Car Color")
        # if color.isValid():
        #     self.color_input.setText(color.name())

    def _populate_initial_data(self) -> None:
        """Populate form fields with initial data (for EDIT mode)."""
        raise NotImplementedError("Initial data population not implemented yet.")

    def _validate(self) -> tuple[bool, str]:
        """Validate car form input."""
        # # Name validation
        # name = self.name_input.text().strip()
        # if not name:
        #     return False, "Name cannot be empty."
        #
        # # Road selection validation
        # if self.road_combo.currentIndex() < 0:
        #     return False, "Please select a road."
        #
        # # Color validation
        # color = self.color_input.text().strip()
        # if not color or not color.startswith('#') or len(color) != 7:
        #     return False, "Color must be in #RRGGBB format."
        #
        # # Length validation
        # if self.length_spin.value() <= 0:
        #     return False, "Length must be positive."
        #
        # return True, ""

    def _collect_data(self) -> dict:
        """Collect car data from form fields."""
        # selected_road = self.road_combo.currentData()
        # lane_index = int(self.lane_index_spin.value())
        # lane_direction = self.lane_direction_combo.currentData()
        #
        # lane = Lane(
        #     road=selected_road,
        #     lane_index=lane_index,
        #     lane_direction=lane_direction
        # )
        #
        # return {
        #     'name': self.name_input.text().strip(),
        #     'lane': lane,
        #     'color': self.color_input.text().strip(),
        #     'position_on_lane': self.position_spin.value(),
        #     'transition': self.transition_spin.value(),
        #     'velocity': self.velocity_spin.value(),
        #     'length': self.length_spin.value(),
        #     'next_turn': None  # TODO: Implement turn intent selection
        # }

    def accept(self) -> None:
        """Override accept to emit car_confirmed signal with CarParams."""
        # data = self._collect_data()
        # car_params = CarParams(**data)
        # self.car_confirmed.emit(car_params)
        # super().accept()

