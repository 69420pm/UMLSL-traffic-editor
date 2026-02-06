"""
Edit query dialog for the UMLSL Traffic Editor.

Provides a dialog window for creating and editing query entities.
"""
import html

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtGui import QResizeEvent, Qt
from PySide6.QtWidgets import QDialog, QLabel

from pse.umlsl_editor.src.model.errors.umlsl_query_errors import (
    UMLSLQueryValidationError,
)
from pse.umlsl_editor.src.query.evaluator import UMLSLEvaluator, ParserError
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog
from pse.umlsl_editor.src.view.ui.lists.confirm_deletion_dialog import (
    ConfirmDeletionDialog,
)
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

        if not self._cars_dict:
            self._is_valid = False
            return

        self._is_valid = True
        self._cars_list = list(self._cars_dict.values())

        self._populate_fields()
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        self.b_save.clicked.connect(self.accept)
        self.b_delete.clicked.connect(self._on_delete_clicked)

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

        self.t_umlsl.document().contentsChanged.connect(self.textChanged)

    def textChanged(self) -> None:
        self.render_latex()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.render_latex()

    def render_latex(self):
        latex_label = self.findChild(QLabel, "l_preview")
        latex_label.setStyleSheet("color: white;")
        if latex_label is None:
            return

        input = self.t_umlsl.toPlainText()
        if input.strip() == "":
            latex_label.setText("No input")
            return

        latex_code: str
        try:
            latex_code = UMLSLEvaluator(self._application_controller.get_traffic_snapshot_reader()).compute_latex(input)
        except ParserError as e:
            input = e.input
            text = input
            print("write error")

            pre_scope = html.escape(text[:e.scope_start])
            scope = html.escape(text[e.scope_start:e.scope_end])
            post_scope = html.escape(text[e.scope_end:])

            caret_indent = " " * len(text[:e.scope_start])
            caret_marker = "^" * len(text[e.scope_start:e.scope_end])
            caret_line = caret_indent + caret_marker

            error_html = (
                f'<div style="font-family: \'Consolas\', \'Courier New\', monospace; '
                f'font-size: 14px; white-space: pre; color: white;">'
                f'{pre_scope}'
                f'<span style="color: red; font-weight: bold;">{scope}</span>'
                f'{post_scope}<br>'
                f'<span style="color: red;">{caret_line}: error originates here</span><br>'
                f'<span style="color: red;">{e.reason}</span>'
            )
            error_html += '</div>'

            latex_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            latex_label.setText(error_html)
            print(error_html)
          #  latex_label.setStyleSheet("color: red;")
            return
        except Exception as e:
            message = e.args[0].replace("\n", "<br>'")

            precise_error = f"""
            <table align="center">
                <tr>
                    <td style="white-space: pre">{message}</td>
                </tr>
            </table>
            """

            latex_label.setText(precise_error)
            latex_label.setStyleSheet("color: red;")
            print(e)
            return

        max_width = latex_label.width() * 0.95
        try:
            pixmap = latex_to_pixmap(latex_code, font_size=20, color="#FFFFFF", max_width=max_width)
            latex_label.setPixmap(pixmap)
            latex_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            latex_label.setScaledContents(False)
        except Exception as e:
            latex_label.setText("Error converting LaTeX to image")
            print(e)

    def _on_delete_clicked(self) -> None:
        """Handle delete action for existing queries."""
        if not self._is_edit or self._query is None:
            return

        # Confirm deletion with the user
        confirm = ConfirmDeletionDialog(
            f"Are you sure you want to delete this query?",
            self,
        ).exec()

        if confirm == 1:
            # Defer deletion to next event loop iteration to allow QML signal
            # handlers to complete before the underlying data is destroyed.
            query_uid = self._query.uid
            QTimer.singleShot(0, lambda: self._application_controller.command_controller.remove_umlsl_query(query_uid))
            self.accept()

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
        latex = self.t_umlsl.text()

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

        super().accept()
