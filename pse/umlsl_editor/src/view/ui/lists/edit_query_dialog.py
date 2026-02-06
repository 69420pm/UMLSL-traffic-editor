"""
Edit query dialog for the UMLSL Traffic Editor.

Provides a dialog window for creating and editing query entities.
"""

from typing import TYPE_CHECKING

from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import QDialog, QLabel

from pse.umlsl_editor.src.query.evaluator import UMLSLEvaluator
from pse.umlsl_editor.src.view.ui.lists.latex_renderer import latex_to_pixmap

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
        self._cars_list = list(self._cars_dict.values())

        self._populate_fields()

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

        self.t_umlsl.document().contentsChanged.connect(self.textChanged)

    def textChanged(self) -> None:
        self.render_latex()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.render_latex()

    def render_latex(self) :
        latex_label = self.findChild(QLabel, "l_preview")
        if latex_label is None:
            return

        input = self.t_umlsl.toPlainText()
        latex_code = UMLSLEvaluator(self._application_controller.get_traffic_snapshot_reader()).compute_latex(input)
        max_width = latex_label.width() * 0.95
        try:
            my_latex = latex_code
            pixmap = latex_to_pixmap(my_latex, font_size=20, color="#FFFFFF", max_width=max_width)
            latex_label.setPixmap(pixmap)
            latex_label.setScaledContents(False)
        except Exception as e:
            print(e)

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

        super().accept()
