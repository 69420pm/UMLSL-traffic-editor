from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_query_dialog import Ui_Edit_Query_Dialog


class EditQueryDialog(QDialog, Ui_Edit_Query_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)