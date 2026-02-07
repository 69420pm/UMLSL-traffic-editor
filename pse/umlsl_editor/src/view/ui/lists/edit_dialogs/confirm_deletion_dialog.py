from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_delete_dialog import (
    Ui_Delete_Dialog,
)


class ConfirmDeletionDialog(QDialog, Ui_Delete_Dialog):
    """

    """

    def __init__(
            self,
            message: str,
            parent=None,
            title: str | None = None,
            confirm_text: str | None = None,
            cancel_text: str | None = None,
    ):
        """

        """
        super().__init__(parent)
        self.setupUi(self)
        if title:
            self.setWindowTitle(title)
        if confirm_text:
            self.b_delete.setText(confirm_text)
        if cancel_text:
            self.b_cancel.setText(cancel_text)
        self.l_content.setText(message)
