"""
Edit query dialog for the UMLSL Traffic Editor.

Provides a dialog window for creating and editing query entities.
"""

import html
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtGui import QFontDatabase, QImage, QPixmap, QResizeEvent, Qt
from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.model.errors.umlsl_query_errors import (
    UMLSLQueryValidationError,
)
from pse.umlsl_editor.src.query.evaluator import ParserError, UMLSLEvaluator
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog
from pse.umlsl_editor.src.view.ui.lists.confirm_deletion_dialog import (
    ConfirmDeletionDialog,
)
from pse.umlsl_editor.src.view.ui.lists.latex_renderer import latex_to_bytes
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_query_dialog import (
    Ui_Edit_Query_Dialog,
)

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController


class LatexRenderWorker(QObject):
    """
    Worker that renders LaTeX strings to image bytes in a background thread.

    This worker uses the Agg backend which is thread-safe and doesn't require
    access to the GUI/main thread.

    Signals:
        finished: Emitted when rendering is complete, with the resulting image bytes.
        error: Emitted when an error occurs, with the error message.
    """

    finished = Signal(bytes)
    error = Signal(str)

    def __init__(
            self,
            latex_code: str,
            font_size: int = 20,
            color: str = "#FFFFFF",
            dpi: int = 300,
    ) -> None:
        """
        Initialize the render worker.

        Args:
            latex_code: The LaTeX code to render.
            font_size: Font size for rendering.
            color: Text color for rendering.
            dpi: Resolution of the output image.
        """
        super().__init__()
        self._latex_code = latex_code
        self._font_size = font_size
        self._color = color
        self._dpi = dpi

    def run(self) -> None:
        """Perform the LaTeX rendering."""
        try:
            image_bytes = latex_to_bytes(
                self._latex_code,
                font_size=self._font_size,
                color=self._color,
                dpi=self._dpi,
            )
            self.finished.emit(image_bytes)
        except Exception as e:
            self.error.emit(str(e))


class EditQueryDialog(QDialog, Ui_Edit_Query_Dialog):
    """
    Dialog for creating and editing query entities.

    This dialog provides a user interface for modifying query properties.
    It inherits from both QDialog for dialog behavior and Ui_Edit_Query_Dialog
    for the auto-generated UI layout.

    Attributes:
        _query: The query entity being edited or created.
        _is_edit: True if editing an existing query, False if creating a new one.
        _application_controller: Reference to the application controller for commands.
        _cars_dict: Dictionary of all available cars keyed by UID.
        _cars_list: List of all available cars for indexing.
        _is_valid: Whether the dialog has valid state (cars available).
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

        # Threading state
        self._render_thread: QThread | None = None
        self._render_worker: LatexRenderWorker | None = None

        # Store device pixel ratio for pixmap conversion on main thread
        self._device_pixel_ratio: float = 1.0
        self._max_width: int | None = None
        self._max_height: int | None = None

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
        self.t_umlsl.document().contentsChanged.connect(self._render_latex)

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
            "Queries require a car to evaluate against.\n"
            "Please add a car to your scene first.",
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
            for i, car in enumerate(self._cars_list):
                if car.uid == self._query.assigned_car_uid:
                    self.d_car.setCurrentIndex(i)
                    break
        elif self._cars_list:
            self.d_car.setCurrentIndex(0)

    def _populate_umlsl_field(self) -> None:
        """Populate the UMLSL text field with the current query string."""
        if self._is_edit and self._query is not None:
            self.t_umlsl.setText(self._query.latex)
        else:
            self.t_umlsl.setText("")

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle resize events by re-rendering the LaTeX preview."""
        super().resizeEvent(event)
        self._render_latex()

    def _render_latex(self) -> None:
        """Render the LaTeX preview."""
        user_input = self.t_umlsl.toPlainText()

        if not user_input.strip():
            self.l_preview.setText("No input")
            return

        try:
            evaluator = UMLSLEvaluator(
                self._application_controller.get_traffic_snapshot_reader()
            )
            latex_code = evaluator.compute_latex(user_input)
        except ParserError as e:
            self._display_parser_error(user_input, e)
            return
        except Exception as e:
            self._display_generic_error(e)
            return

        self._start_render_thread(latex_code)

    def _start_render_thread(self, latex_code: str) -> None:
        """Start a background thread to render the LaTeX pixmap."""
        # Clean up any existing render thread
        self._cleanup_render_thread()

        # Store dimensions for use when converting bytes to pixmap on main thread
        self._max_width = int(self.l_preview.width() * 0.9)
        self._max_height = int(self.l_preview.height() * 0.8)
        self._device_pixel_ratio = self.devicePixelRatioF()

        # Create worker and thread
        self._render_thread = QThread()
        self._render_worker = LatexRenderWorker(
            latex_code=latex_code,
            font_size=10,
            color="#F9F9F9",
            dpi=300,
        )
        self._render_worker.moveToThread(self._render_thread)

        # Connect signals
        self._render_thread.started.connect(self._render_worker.run)
        self._render_worker.finished.connect(self._on_render_finished)
        self._render_worker.error.connect(self._on_render_error)
        self._render_worker.finished.connect(self._render_thread.quit)
        self._render_worker.error.connect(self._render_thread.quit)

        # Start rendering
        self._render_thread.start()

    def _cleanup_render_thread(self) -> None:
        """Clean up the render thread if it exists."""
        if self._render_thread is not None:
            if self._render_thread.isRunning():
                self._render_thread.quit()
                self._render_thread.wait(100)  # Wait up to 100ms
            self._render_thread.deleteLater()
            self._render_thread = None

        if self._render_worker is not None:
            self._render_worker.deleteLater()
            self._render_worker = None

    def _on_render_finished(self, image_bytes: bytes) -> None:
        """
        Handle successful LaTeX render completion.

        Converts the image bytes to a QPixmap on the main thread (thread-safe).

        Args:
            image_bytes: The PNG image data from the worker thread.
        """
        if not image_bytes:
            self.l_preview.setText("Error rendering LaTeX")
            return

        # Convert bytes to QPixmap on the main thread (thread-safe)
        qimg = QImage.fromData(image_bytes)
        if qimg.isNull():
            self.l_preview.setText("Error converting image")
            return

        pixmap = QPixmap.fromImage(qimg)

        # Scale to fit within the preview area
        pixmap = self._scale_pixmap_to_fit(pixmap, self._max_width, self._max_height)

        # Set device pixel ratio for high-DPI displays
        if self._device_pixel_ratio != 1.0:
            pixmap.setDevicePixelRatio(self._device_pixel_ratio)

        self.l_preview.setPixmap(pixmap)
        self.l_preview.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        self.l_preview.setScaledContents(False)

    def _scale_pixmap_to_fit(
            self,
            pixmap: QPixmap,
            max_width: int | None,
            max_height: int | None,
    ) -> QPixmap:
        """
        Scale a pixmap to fit within the given max dimensions while preserving aspect ratio.

        Only scales down if the pixmap exceeds the max dimensions. Does not scale up.

        Args:
            pixmap: The pixmap to scale.
            max_width: Maximum width. If None, no width limit.
            max_height: Maximum height. If None, no height limit.

        Returns:
            The scaled pixmap.
        """
        if pixmap.isNull():
            return pixmap

        current_width = pixmap.width()
        current_height = pixmap.height()

        # Calculate scale factors for each dimension
        width_scale = 1.0
        height_scale = 1.0

        if max_width is not None and current_width > max_width:
            width_scale = max_width / current_width

        if max_height is not None and current_height > max_height:
            height_scale = max_height / current_height

        # Use the smaller scale factor to ensure we fit within both constraints
        scale = min(width_scale, height_scale)

        if scale < 1.0:
            new_width = int(current_width * scale)
            new_height = int(current_height * scale)
            pixmap = pixmap.scaled(
                new_width,
                new_height,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )

        return pixmap

    def _on_render_error(self, error_message: str) -> None:
        """Handle LaTeX render error."""
        self.l_preview.setText("Error converting LaTeX to image")
        print(f"LaTeX rendering error: {error_message}")

    def _display_parser_error(self, user_input: str, error: ParserError) -> None:
        """Display a parser error with syntax highlighting."""
        pre_err = html.escape(user_input[: error.scope_start])
        err = html.escape(user_input[error.scope_start: error.scope_end])
        post_err = html.escape(user_input[error.scope_end:])

        caret_indent = " " * error.scope_start
        caret_marker = "^" * (error.scope_end - error.scope_start)
        caret_line = caret_indent + caret_marker

        # Get system monospace font to avoid font lookup delays
        mono_font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont).family()

        error_html = (
            f'<div style="font-family: \'{mono_font}\'; '
            f'font-size: 14px; white-space: pre-wrap; color: white;">'
            f"{pre_err}"
            f'<span style="color: red; font-weight: bold;">{err}</span>'
            f"{post_err}<br>"
            f'<span style="color: red;">{caret_line}: {error.reason}</span><br>'
        )

        if error.help is not None:
            error_html += f'<span style="color: red;">Help: {error.help}.</span>'

        error_html += "</div>"

        self.l_preview.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.l_preview.setText(error_html)

    def _display_generic_error(self, error: Exception) -> None:
        """Display a generic error message."""
        self.l_preview.setText(f"Error: {error}")
        print(f"LaTeX parsing error: {error}")

    def _on_delete_clicked(self) -> None:
        """Handle delete action for existing queries."""
        if not self._is_edit or self._query is None:
            return

        confirm = ConfirmDeletionDialog(
            "Are you sure you want to delete this query?",
            self,
        ).exec()

        if confirm == 1:
            query_uid = self._query.uid
            QTimer.singleShot(
                0,
                lambda: self._application_controller.command_controller.remove_umlsl_query(
                    query_uid
                ),
            )
            self.accept()

    def accept(self) -> None:
        """
        Handle dialog acceptance by saving query changes.

        If editing an existing query, updates its properties. If creating
        a new query, adds it to the queries model. Then closes the dialog.
        """
        self._cleanup_render_thread()

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

    def reject(self) -> None:
        """Handle dialog rejection by cleaning up resources."""
        self._cleanup_render_thread()
        super().reject()

    def closeEvent(self, event) -> None:
        """Handle dialog close by cleaning up resources."""
        self._cleanup_render_thread()
        super().closeEvent(event)
