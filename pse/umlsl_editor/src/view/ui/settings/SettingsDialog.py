"""
Settings dialog for the UMLSL Traffic Editor.

Provides a dialog window for configuring application settings.
"""

from PySide6.QtWidgets import QDialog

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

    def __init__(self, parent=None):
        """
        Initialize the settings dialog.

        Args:
            parent: The parent widget for this dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setupUi(self)
