from PySide6.QtWidgets import QDialog, QWidget

from pse.umlsl_editor.src.view.ui_utils import load_ui


class SettingsDialogController:
    def __init__(self, parent: QWidget, settings_vgit iewmodel):
        self._parent = parent
        self._settings_vm = settings_viewmodel
        self._dialog: QDialog | None = None

    def open(self) -> None:
        if self._dialog is None:
            self._dialog = QDialog(self._parent)
            self._ui = load_ui("../../widgets/settings_dialog.ui")
            self._ui.setupUi(self._dialog)
            self._bind_to_viewmodel()
        self._dialog.exec()

    def _bind_to_viewmodel(self) -> None:
        # Bind UI widgets to viewmodel properties
        self._ui.c_savty_space.setChecked(self._settings_vm.show_safety_space)
        self._ui.c_coordinate_system.setChecked(self._settings_vm.show_coordinates)
        # Connect changes back to viewmodel
        self._ui.c_savty_space.toggled.connect(self._settings_vm.set_show_safety_space)
