"""
Global controls for the UMLSL Traffic Editor.

Handles global UI actions such as save, open, and settings from the main menu bar.
"""

from PySide6.QtCore import QObject

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

    def __init__(self, main_window: Ui_MainWindow) -> None:
        """
        Initialize the global controls.

        Args:
            main_window: The main application window containing menu actions.
        """
        super().__init__(main_window)
        self._window = main_window

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
        """Handle the save action."""
        print("Save button clicked")

    def _on_save_as(self) -> None:
        """Handle the save-as action."""
        print("Save As button clicked")

    def _on_open(self) -> None:
        """Handle the open file action."""
        print("Open button clicked")

    def _on_open_settings(self) -> None:
        """Open the application settings dialog."""
        dialog = SettingsDialog(self._window)
        dialog.exec()
