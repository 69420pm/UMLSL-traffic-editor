"""
Global controls for the UMLSL Traffic Editor.

Handles global UI actions such as save, open, and settings from the main menu bar.
"""
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog

from pse.umlsl_editor.src.commands.command import CommandValidationError
from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.errors.errors import BaseError
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog
from pse.umlsl_editor.src.view.ui.settings.settings_dialog import SettingsDialog
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow


class GlobalControls(QObject):
    """
    Controller for global application actions.

    Manages the main menu bar actions including file operations (save, open)
    and application settings. Connects menu actions to their respective handlers.

    Attributes:
        window: Reference to the main application window.
        save_button: Menu action for saving the current file.
        save_as_button: Menu action for saving with a new filename.
        open_button: Menu action for opening a file.
        open_settings_button: Menu action for opening the settings dialog.
    """

    def __init__(self, main_window: Ui_MainWindow, application_controller: "ApplicationController") -> None:
        """
        Initialize the global controls.

        Args:
            main_window: The main application window containing menu actions.
        """
        super().__init__(main_window)
        self._window = main_window
        self.application_controller = application_controller

        self._save_action = self._window.actionSave
        self._save_as_action = self._window.actionSave_As
        self._open_action = self._window.actionOpen
        self._settings_action = self._window.actionSettings

        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect menu action signals to their handler methods."""
        self._save_action.triggered.connect(self._on_save)
        self._save_as_action.triggered.connect(self._on_save_as)
        self._open_action.triggered.connect(self._on_open)
        self._settings_action.triggered.connect(self._on_open_settings)

    def _on_save(self) -> None:
        """Check if the current snapshot can be saved."""
        if self.application_controller.command_controller.get_current_snapshot_path() is None:
            self._on_save_as()
        else:
            try:
                self.application_controller.command_controller.save_traffic_snapshot()
            except CommandValidationError as exc:
                WarningDialog("Can not save file", str(exc), self._window).exec()

    def _on_save_as(self) -> None:
        file_name, _ = QFileDialog.getSaveFileName(
            None,
            "Save current snapshot",
            "",
            "JSON Files (*.json)"
        )
        if not file_name:
            return
        try:
            self.application_controller.command_controller.save_as_traffic_snapshot(file_name)
        except CommandValidationError as exc:
            WarningDialog("Can not save file", str(exc), self._window).exec()

        self._window.update_main_window_title()

    def _on_open(self) -> None:
        file_name, _ = QFileDialog.getOpenFileName(
            None,
            "Open new snapshot",
            "",
            "JSON Files (*.json)"
        )
        if not file_name:
            return
        try:
            self.application_controller.command_controller.load_traffic_snapshot(file_name)
        except (BaseError, CommandValidationError) as exc:
            WarningDialog("Can not open file", str(exc), self._window).exec()

        self._window.update_main_window_title()

    def _on_open_settings(self) -> None:
        """Open the application settings dialog."""
        dialog = SettingsDialog(application_controller=self.application_controller, parent=self._window)
        dialog.exec()
