from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_car_dialog import Ui_Edit_Car_Dialog

class EditCarDialog(QDialog, Ui_Edit_Car_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)