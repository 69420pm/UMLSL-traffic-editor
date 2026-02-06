"""
Settings dialog for the UMLSL Traffic Editor.

Provides a dialog window for configuring application settings.
"""

from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_settings_dialog import (
    Ui_Settings_Dialog,
)


class SettingsDialog(QDialog, Ui_Settings_Dialog):
    """
    Dialog for configuring application settings.

    This dialog provides a user interface for modifying application preferences
    and configuration options. It inherits from both QDialog for dialog behavior
    and Ui_Settings_Dialog for the auto-generated UI layout.

    Attributes:
        Inherits all attributes from QDialog and Ui_Settings_Dialog.
    """

    def __init__(self, application_controller: "ApplicationController", parent=None):
        """
        Initialize the settings dialog.

        Args:
            parent: The parent widget for this dialog. Defaults to None.
        """
        super().__init__(parent)
        self._application_controller = application_controller
        self.setupUi(self)

        self.c_coordinate_system.clicked.connect(self._on_toggle_coordinate_system)
        self.c_coordinate_system.setChecked(
            self._application_controller.view_event_handler.should_render_coordinate_system)

        self.c_grid.clicked.connect(self._on_toggle_grid)
        self.c_grid.setChecked(self._application_controller.view_event_handler.should_render_grid)

        self.c_savty_space.clicked.connect(self._on_toggle_safety_distance)
        self.c_savty_space.setChecked(self._application_controller.view_event_handler.should_render_safety_distance)

        self.s_braking.setValue(self._application_controller.command_controller.settings_model.breaking_deceleration)
        self.s_braking.valueChanged.connect(self._on_braking_changed)
        self.s_accerleration.setValue(self._application_controller.command_controller.settings_model.max_acceleration)
        self.s_accerleration.valueChanged.connect(self._on_acceleration_changed)

    def _on_braking_changed(self):
        self._application_controller.command_controller.settings_model.set_breaking_deceleration(
            self.s_braking.value()
        )

    def _on_acceleration_changed(self):
        self._application_controller.command_controller.settings_model.set_max_acceleration(
            self.s_accerleration.value()
        )

    def _on_toggle_coordinate_system(self):
        """Handle the toggle of coordinate system rendering."""
        is_checked = self.c_coordinate_system.isChecked()
        self._application_controller.view_event_handler.set_coordinate_system(is_checked)

    def _on_toggle_grid(self):
        """Handle the toggle of coordinate system rendering."""
        is_checked = self.c_grid.isChecked()
        self._application_controller.view_event_handler.set_grid(is_checked)

    def _on_toggle_safety_distance(self):
        """Handle the toggle of safety distance rendering."""
        is_checked = self.c_savty_space.isChecked()
        self._application_controller.view_event_handler.set_safety_distance(is_checked)
