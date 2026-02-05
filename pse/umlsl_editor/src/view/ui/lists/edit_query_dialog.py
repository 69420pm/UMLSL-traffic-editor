"""
Edit query dialog for the UMLSL Traffic Editor.

Provides a dialog window for creating and editing query entities.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.model.errors.umlsl_query_errors import (
    UMLSLQueryValidationError,
)
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_query_dialog import (
    Ui_Edit_Query_Dialog,
)


class EditQueryDialog(QDialog, Ui_Edit_Query_Dialog):
    """
    Dialog for creating and editing query entities.

    This dialog provides a user interface for modifying query properties.
    It inherits from both QDialog for dialog behavior and Ui_Edit_Query_Dialog
    for the auto-generated UI layout.

    Attributes:
        query: The query entity being edited or created.
        is_edit: True if editing an existing query, False if creating a new one.
        application_controller: Reference to the application controller for commands.
        cars_dict: Dictionary of all available cars keyed by UID.
        cars_list: List of all available cars for indexing.
    """

    def __init__(
            self,
            query: UMLSLQuery | None,
            application_controller: "ApplicationController",
            parent=None,
    ) -> None:
        """
        Initialize the edit query dialog.

        Args:
            query: The query to edit, or None to create a new query.
            application_controller: The application controller for executing commands.
            parent: The parent widget for this dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setupUi(self)

        self._query = query
        self._is_edit = query is not None
        self._application_controller = application_controller

        self._cars_dict = application_controller.data_controller.get_all_cars()

        if not self._cars_dict:
            self._is_valid = False
            return

        self._is_valid = True
        self._cars_list = list(self._cars_dict.values())

        self._populate_fields()

    def exec(self) -> int:
        """
        Execute the dialog.

        Returns:
            QDialog.Rejected if the dialog is invalid, otherwise the result of exec().
        """
        if not self._is_valid:
            QTimer.singleShot(0, self._show_no_cars_warning)
            return QDialog.DialogCode.Rejected
        return super().exec()

    def _show_no_cars_warning(self) -> None:
        """Show a warning message that no cars are available."""
        dialog = WarningDialog(
            "Car Required",
            "Queries require a car to evaluate against.\nPlease add a car to your scene first.",
            self.parent(),
        )
        dialog.exec()

    def _populate_fields(self) -> None:
        """Populate dialog fields with the current query's values."""
        self._populate_car_dropdown()
        self._populate_umlsl_field()

    def _populate_car_dropdown(self) -> None:
        """Populate the car selection dropdown with all available cars."""
        self.d_car.clear()
        self.d_car.addItems([car.name for car in self._cars_list])

        if self._is_edit and self._query is not None:
            # Find the index of the current ego car
            for i, car in enumerate(self._cars_list):
                if car.uid == self._query.assigned_car_uid:
                    self.d_car.setCurrentIndex(i)
                    break
        elif self._cars_list:
            # Default to first car if creating new query
            self.d_car.setCurrentIndex(0)

    def _populate_umlsl_field(self) -> None:
        """Populate the UMLSL text field with the current query string."""
        if self._is_edit and self._query is not None:
            self.t_umlsl.setText(self._query.latex)
        else:
            self.t_umlsl.setText("")

    def accept(self) -> None:
        """
        Handle dialog acceptance by saving query changes.

        If editing an existing query, updates its properties. If creating
        a new query, adds it to the queries model. Then closes the dialog.
        """
        selected_car_index = self.d_car.currentIndex()
        if selected_car_index < 0 or selected_car_index >= len(self._cars_list):
            super().reject()
            return

        selected_car = self._cars_list[selected_car_index]
        latex = self.t_umlsl.toPlainText()

        try:
            if self._is_edit and self._query is not None:
                self._application_controller.command_controller.update_umlsl_query(
                    query=self._query,
                    assigned_car_name=selected_car.uid,
                    latex=latex,
                )
            else:
                self._application_controller.command_controller.add_umlsl_query(
                    assigned_car_name=selected_car.uid,
                    latex=latex,
                )
        except UMLSLQueryValidationError as e:
            dialog = WarningDialog(
                "Validation Error",
                str(e),
                self,
            )
            dialog.exec()
            return

        super().accept()
