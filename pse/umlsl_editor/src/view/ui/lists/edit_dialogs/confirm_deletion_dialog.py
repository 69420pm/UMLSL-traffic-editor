from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_delete_dialog import Ui_Delete_Dialog


class ConfirmDeletionDialog(QDialog, Ui_Delete_Dialog):
    """

    """

    def __init__(self, message: str, parent=None):
        """

        """
        super().__init__(parent)
        self.setupUi(self)
        self.l_content.setText(message)
