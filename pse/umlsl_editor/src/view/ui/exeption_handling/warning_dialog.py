from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_error_dialog import Ui_Error_Dialog


class WarningDialog(QDialog, Ui_Error_Dialog):
    """
    Dialog for displaying warning messages to the user.

    This dialog provides a simple interface for showing warning messages. It inherits
    from both QDialog for dialog behavior and Ui_Error_Dialog for the auto-generated
    UI layout.

    Attributes:
        Inherits all attributes from QDialog and Ui_Error_Dialog.
    """

    def __init__(self, title: str, message: str, parent=None):
        """
        Initialize the warning dialog.

        Args:
            message: The warning message to display in the dialog.
            parent: The parent widget for this dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setupUi(self)
        self.l_titel.setText(title)
        self.l_content.setText(message)
