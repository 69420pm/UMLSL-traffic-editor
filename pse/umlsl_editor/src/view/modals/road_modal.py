"""
Modal dialog for creating and editing roads.
"""
from typing import Optional, Callable

from PySide6.QtWidgets import (
    QLineEdit, QDoubleSpinBox, QComboBox, QWidget, QSpinBox
)
from PySide6.QtCore import Signal

from pse.umlsl_editor.src.core.dataclasses.road import RoadParams, RoadOrientation
from pse.umlsl_editor.src.view.modals.entity_modal import EntityModal, ModalMode


class RoadModal(EntityModal):
    """
    Modal dialog for creating or editing a road.

    Provides form fields for all road attributes and emits a RoadParams
    object when the user confirms the dialog.
    """

    # Signal emitted when user confirms road creation/editing
    road_confirmed = Signal(RoadParams)

    def __init__(
        self,
        mode: ModalMode = ModalMode.CREATE,
        initial_data: Optional[dict] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the road modal.

        Args:
            mode: Operation mode (CREATE or EDIT).
            initial_data: Initial values for form fields (used in EDIT mode).
            parent: Parent widget.
        """
        # self.initial_data = initial_data or {}
        #
        # title = "Edit Road" if mode == ModalMode.EDIT else "Create Road"
        # super().__init__(title, mode, parent)
        #
        # # Populate initial data if in EDIT mode
        # if mode == ModalMode.EDIT and initial_data:
        #     self._populate_initial_data()

    def _setup_form(self) -> None:
        """Setup form fields for road attributes."""
        # # Name
        # self.name_input = QLineEdit()
        # self.form_layout.addRow("Name:", self.name_input)
        #
        # # Orientation
        # self.orientation_combo = QComboBox()
        # self.orientation_combo.addItem("Horizontal", RoadOrientation.HORIZONTAL)
        # self.orientation_combo.addItem("Vertical", RoadOrientation.VERTICAL)
        # self.form_layout.addRow("Orientation:", self.orientation_combo)
        #
        # # Position
        # self.position_spin = QDoubleSpinBox()
        # self.position_spin.setMinimum(-10000.0)
        # self.position_spin.setMaximum(10000.0)
        # self.position_spin.setDecimals(2)
        # self.form_layout.addRow("Position:", self.position_spin)
        #
        # # Forward lanes
        # self.forward_lanes_spin = QSpinBox()
        # self.forward_lanes_spin.setMinimum(0)
        # self.forward_lanes_spin.setMaximum(10)
        # self.forward_lanes_spin.setValue(1)
        # self.form_layout.addRow("Forward Lanes:", self.forward_lanes_spin)
        #
        # # Backward lanes
        # self.backward_lanes_spin = QSpinBox()
        # self.backward_lanes_spin.setMinimum(0)
        # self.backward_lanes_spin.setMaximum(10)
        # self.backward_lanes_spin.setValue(1)
        # self.form_layout.addRow("Backward Lanes:", self.backward_lanes_spin)

    def _populate_initial_data(self) -> None:
        """Populate form fields with initial data (for EDIT mode)."""
        raise NotImplementedError("Initial data population not implemented yet.")

    def _validate(self) -> tuple[bool, str]:
        """Validate road form input."""
        # # Name validation
        # name = self.name_input.text().strip()
        # if not name:
        #     return False, "Name cannot be empty."
        #
        # # Lane count validation
        # forward_lanes = self.forward_lanes_spin.value()
        # backward_lanes = self.backward_lanes_spin.value()
        # if forward_lanes == 0 and backward_lanes == 0:
        #     return False, "Road must have at least one lane (forward or backward)."
        #
        # return True, ""

    def _collect_data(self) -> dict:
        """Collect road data from form fields."""
        # return {
        #     'name': self.name_input.text().strip(),
        #     'orientation': self.orientation_combo.currentData(),
        #     'position': self.position_spin.value(),
        #     'forward_lanes': self.forward_lanes_spin.value(),
        #     'backward_lanes': self.backward_lanes_spin.value()
        # }

    def accept(self) -> None:
        """Override accept to emit road_confirmed signal with RoadParams."""
        # data = self._collect_data()
        # road_params = RoadParams(**data)
        # self.road_confirmed.emit(road_params)
        # super().accept()

