"""
Base modal dialog class for entity creation and editing.
"""
from enum import Enum
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QWidget
)
from PySide6.QtCore import Qt, Signal


class ModalMode(Enum):
    """Enumeration for modal operation modes."""
    CREATE = "create"
    EDIT = "edit"


class EntityModal(QDialog):
    """
    Base class for entity creation/editing modals.

    Provides common UI patterns:
    - Form layout for input fields
    - OK/Cancel buttons
    - Validation error display
    - Mode handling (CREATE vs EDIT)

    Subclasses should:
    1. Override _setup_form() to add specific input fields
    2. Override _validate() to implement validation logic
    3. Override _collect_data() to gather form data
    4. Define a Signal to emit collected data on confirmation
    """

    def __init__(
        self,
        title: str,
        mode: ModalMode = ModalMode.CREATE,
        parent: Optional[QWidget] = None
    ):
        """
        Initialize the entity modal.

        Args:
            title: Window title for the dialog.
            mode: Operation mode (CREATE or EDIT).
            parent: Parent widget.
        """
        super().__init__(parent)
        self.mode = mode
        self.setWindowTitle(title)
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize the UI components."""
        # # Main layout
        # main_layout = QVBoxLayout(self)
        #
        # # Form layout for input fields
        # self.form_layout = QFormLayout()
        # main_layout.addLayout(self.form_layout)
        #
        # # Subclass adds specific form fields
        # self._setup_form()
        #
        # # Error message label (hidden by default)
        # self.error_label = QLabel()
        # self.error_label.setStyleSheet("color: red;")
        # self.error_label.setWordWrap(True)
        # self.error_label.hide()
        # main_layout.addWidget(self.error_label)
        #
        # # Button box
        # button_layout = QHBoxLayout()
        # button_layout.addStretch()
        #
        # self.ok_button = QPushButton("OK")
        # self.ok_button.clicked.connect(self._on_ok_clicked)
        # self.ok_button.setDefault(True)
        # button_layout.addWidget(self.ok_button)
        #
        # self.cancel_button = QPushButton("Cancel")
        # self.cancel_button.clicked.connect(self.reject)
        # button_layout.addWidget(self.cancel_button)
        #
        # main_layout.addLayout(button_layout)
        #
        # # Set reasonable default size
        # self.resize(400, 300)

    def _setup_form(self) -> None:
        """
        Setup form fields. Override in subclasses.

        Example:
            self.name_input = QLineEdit()
            self.form_layout.addRow("Name:", self.name_input)
        """
        raise NotImplementedError("Subclasses must implement _setup_form()")

    def _validate(self) -> tuple[bool, str]:
        """
        Validate form input.

        Returns:
            Tuple of (is_valid, error_message).
            If valid, error_message should be empty.

        Example:
            if not self.name_input.text().strip():
                return False, "Name cannot be empty"
            return True, ""
        """
        raise NotImplementedError("Subclasses must implement _validate()")

    def _collect_data(self) -> dict:
        """
        Collect data from form fields.

        Returns:
            Dictionary of field names to values.

        Example:
            return {
                'name': self.name_input.text().strip(),
                'value': self.value_spinbox.value()
            }
        """
        raise NotImplementedError("Subclasses must implement _collect_data()")

    def _on_ok_clicked(self) -> None:
        """Handle OK button click with validation."""
        # # Validate input
        # is_valid, error_message = self._validate()
        #
        # if not is_valid:
        #     self._show_error(error_message)
        #     return
        #
        # # Hide error if previously shown
        # self._hide_error()
        #
        # # Accept dialog (subclass signal emission happens via accept())
        # self.accept()

    def _show_error(self, message: str) -> None:
        """Display validation error message."""
        # self.error_label.setText(message)
        # self.error_label.show()

    def _hide_error(self) -> None:
        """Hide validation error message."""
        # self.error_label.hide()

    def get_data(self) -> Optional[dict]:
        """
        Get collected form data after dialog is accepted.

        Returns:
            Dictionary of form data if dialog was accepted, None otherwise.
        """
        # if self.result() == QDialog.DialogCode.Accepted:
        #     return self._collect_data()
        # return None

