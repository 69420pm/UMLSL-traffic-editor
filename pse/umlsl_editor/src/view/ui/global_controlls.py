from PySide6.QtCore import QObject

from pse.umlsl_editor.src.view.ui.settings.SettingsDialog import SettingsDialog
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_main import Ui_MainWindow



class GlobalControls(QObject):
    def __init__(self, main_window:Ui_MainWindow) -> None:
        super().__init__(main_window)
        self.window = main_window

        self.save_button = self.window.actionSave
        self.save_as_button = self.window.actionSave_As
        self.open_button = self.window.actionOpen
        self.open_settings_button = self.window.actionSettings

    def setup_ui(self) -> None:
        """Connect button click signals."""
        self.save_button.triggered.connect(self.on_save_clicked)
        self.save_as_button.triggered.connect(self.on_save_as_clicked)
        self.open_button.triggered.connect(self.on_open_clicked)
        self.open_settings_button.triggered.connect(self.on_settings_open_clicked)

    def on_save_clicked(self) -> None:
        print("Save button clicked")

    def on_save_as_clicked(self) -> None:
        print("Save button clicked")

    def on_open_clicked(self) -> None:
        print("Load button clicked")

    def on_settings_open_clicked(self) -> None:
        dialog = SettingsDialog(self.window)
        dialog.exec()