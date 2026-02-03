"""
Global controls for the UMLSL Traffic Editor.

Handles global UI actions such as save, open, and settings from the main menu bar.
"""
import warnings

from PySide6.QtCore import QObject

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.settings.SettingsDialog import SettingsDialog
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
        warnings.warn("Save functionality not yet implemented.", UserWarning)
        """Else, save as"""
        # self._on_save_as()

    def _on_save_as(self) -> None:
        warnings.warn("Save As functionality not yet implemented.", UserWarning)

        # file_name, _ = QFileDialog.getSaveFileName(None, "Save current snapshot", "", ".json Files (*.json)")

    def _on_open(self) -> None:
        warnings.warn("Open functionality not yet implemented.", UserWarning)

        # file_name, _ = QFileDialog.getOpenFileName(None, "Open new snapshot", "", ".json Files (*.json)")

    def _on_open_settings(self) -> None:
        """Open the application settings dialog."""
        dialog = SettingsDialog(application_controller=self.application_controller, parent=self._window)
        dialog.exec()
