from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_settings_dialog import Ui_Settings_Dialog


class SettingsDialog(QDialog, Ui_Settings_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)