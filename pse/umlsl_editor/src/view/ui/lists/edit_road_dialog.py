from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_road_dialog import Ui_Edit_Road_Dialog


class EditRoadDialog(QDialog, Ui_Edit_Road_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)