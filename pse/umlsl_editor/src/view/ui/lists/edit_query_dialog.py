"""
Edit query dialog for the UMLSL Traffic Editor.

Provides a dialog window for creating and editing query entities.
"""

from PySide6.QtWidgets import QDialog

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
        Inherits all attributes from QDialog and Ui_Edit_Query_Dialog.
    """

    def __init__(self, parent=None):
        """
        Initialize the edit query dialog.

        Args:
            parent: The parent widget for this dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setupUi(self)
