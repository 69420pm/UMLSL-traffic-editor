"""
Modal dialog for creating and editing UMLSL queries.
"""
from typing import Optional, Callable

from PySide6.QtWidgets import (
    QTextEdit, QComboBox, QWidget, QLabel
)
from PySide6.QtCore import Signal

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.view.modals.entity_modal import EntityModal, ModalMode


class QueryModal(EntityModal):
    """
    Modal dialog for creating or editing a UMLSL query.

    Provides form fields for query attributes (LaTeX expression, assigned car)
    and emits query parameters when the user confirms the dialog.
    """

    # Signal emitted when user confirms query creation/editing
    # Emits tuple of (latex: str, assigned_car: Car)
    query_confirmed = Signal(str, Car)

    def __init__(
        self,
        mode: ModalMode = ModalMode.CREATE,
        get_cars: Optional[Callable[[], list[Car]]] = None,
        initial_data: Optional[dict] = None,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the query modal.

        Args:
            mode: Operation mode (CREATE or EDIT).
            get_cars: Callback to retrieve available cars for dropdown.
            initial_data: Initial values for form fields (used in EDIT mode).
            parent: Parent widget.
        """
        # self.get_cars = get_cars or (lambda: [])
        # self.initial_data = initial_data or {}
        #
        # title = "Edit UMLSL Query" if mode == ModalMode.EDIT else "Create UMLSL Query"
        # super().__init__(title, mode, parent)
        #
        # # Populate initial data if in EDIT mode
        # if mode == ModalMode.EDIT and initial_data:
        #     self._populate_initial_data()

    def _setup_form(self) -> None:
        """Setup form fields for query attributes."""
        # # LaTeX expression
        # self.latex_input = QTextEdit()
        # self.latex_input.setPlaceholderText("Enter UMLSL query in LaTeX format...")
        # self.latex_input.setMaximumHeight(150)
        # self.form_layout.addRow("LaTeX Query:", self.latex_input)
        #
        # # Help text
        # help_label = QLabel("Example: \\forall t. \\text{claim}(l_1, t)")
        # help_label.setStyleSheet("color: gray; font-size: 10px;")
        # self.form_layout.addRow("", help_label)
        #
        # # Assigned car
        # self.car_combo = QComboBox()
        # self._populate_cars()
        # self.form_layout.addRow("Assigned Car:", self.car_combo)

    def _populate_cars(self) -> None:
        """Populate car dropdown with available cars."""
        # self.car_combo.clear()
        # cars = self.get_cars()
        # for car in cars:
        #     self.car_combo.addItem(car.name, car)

    def _populate_initial_data(self) -> None:
        """Populate form fields with initial data (for EDIT mode)."""
        raise NotImplementedError("Initial data population not implemented yet.")

    def _validate(self) -> tuple[bool, str]:
        """Validate query form input."""
        # # LaTeX validation
        # latex = self.latex_input.toPlainText().strip()
        # if not latex:
        #     return False, "LaTeX query cannot be empty."
        #
        # # Car selection validation
        # if self.car_combo.currentIndex() < 0:
        #     return False, "Please select a car to assign the query to."
        #
        # return True, ""

    def _collect_data(self) -> dict:
        """Collect query data from form fields."""
        # return {
        #     'latex': self.latex_input.toPlainText().strip(),
        #     'assigned_car': self.car_combo.currentData()
        # }

    def accept(self) -> None:
        """Override accept to emit query_confirmed signal with parameters."""
        # data = self._collect_data()
        # self.query_confirmed.emit(data['latex'], data['assigned_car'])
        # super().accept()

