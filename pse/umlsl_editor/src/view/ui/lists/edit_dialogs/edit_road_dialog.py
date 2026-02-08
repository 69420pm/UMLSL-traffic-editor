"""
Edit road dialog for the UMLSL Traffic Editor.

Provides a dialog for creating new roads or editing existing road properties
such as name, orientation, position, and lane counts.
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.model.errors.road_errors import (
    RoadTrafficSnapshotContextValidationError,
    RoadValidationError,
)
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog
from pse.umlsl_editor.src.view.ui.lists.deletion_checks import (
    get_road_deletion_block_reason,
)
from pse.umlsl_editor.src.view.ui.lists.edit_dialogs.confirm_deletion_dialog import (
    ConfirmDeletionDialog,
)

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_road_dialog import (
    Ui_Edit_Road_Dialog,
)


class EditRoadDialog(QDialog, Ui_Edit_Road_Dialog):
    """
    Dialog for creating or editing road entities.

    This dialog allows users to configure road properties including name,
    orientation (horizontal/vertical), position, and the number of forward
    and backward lanes. When editing an existing road, the dialog is
    pre-populated with the road's current values.

    Attributes:
        road: The road entity being edited or created.
        is_edit: True if editing an existing road, False if creating a new one.
        application_controller: The application controller for executing commands.
    """

    def __init__(
            self,
            road: Road | None,
            application_controller: "ApplicationController",
            parent=None,
    ) -> None:
        """
        Initialize the road edit dialog.

        Args:
            road: The road to edit, or None to create a new road.
            application_controller: The application controller for command execution.
            parent: The parent widget for this dialog. Defaults to None.
        """
        super().__init__(parent)
        self.setupUi(self)

        self._road = road
        self._is_edit = road is not None
        self._application_controller = application_controller

        self._populate_fields()
        self._connect_signals()

    def _connect_signals(self) -> None:
        """Connect UI signals to their handlers."""
        self.b_save.clicked.connect(self._on_save_clicked)
        self.b_delete.clicked.connect(self._on_delete_clicked)

    def _on_save_clicked(self) -> None:
        self.accept()

    def _on_delete_clicked(self) -> None:
        """Handle delete action for existing roads."""
        if not self._is_edit:
            return

        block_reason = get_road_deletion_block_reason(self._application_controller, self._road)
        if block_reason:
            WarningDialog("Deletion Error", block_reason, self).exec()
            return
        # Confirm deletion with the user
        confirm = ConfirmDeletionDialog(
            f"Are you sure you want to delete road '{self._road.name}'?",
            self,
        ).exec()

        if confirm == 1:
            # Defer deletion to next event loop iteration to allow QML signal
            # handlers to complete before the underlying data is destroyed.
            road_uid = self._road.uid
            QTimer.singleShot(0, lambda: self._application_controller.command_controller.remove_road(road_uid))
            self.parent().snackbar.show_message(f"Road '{self._road.name}' deleted successfully.")
            self.accept()

    def _get_default_road_values(self) -> dict:
        """Return default road field values for create mode."""
        return {
            "name": "default",
            "orientation": RoadOrientation.HORIZONTAL,
            "position": 0,
            "number_of_forward_lanes": 1,
            "number_of_backward_lanes": 1,
        }

    def _apply_road_values(
            self,
            *,
            name: str,
            orientation: RoadOrientation,
            position: int,
            number_of_forward_lanes: int,
            number_of_backward_lanes: int,
    ) -> None:
        """Apply road values to the dialog widgets."""
        self.t_name.setText(name)

        self.d_orientation.clear()
        orientations = [orientation.name.lower() for orientation in RoadOrientation]
        self.d_orientation.addItems(orientations)
        self.d_orientation.setCurrentIndex(orientation.value)

        self.s_position.setValue(position)
        self.s_forward.setValue(number_of_forward_lanes)
        self.s_backward.setValue(number_of_backward_lanes)

    def _populate_fields(self) -> None:
        """Populate dialog fields with the current road's values."""
        if not self._is_edit:
            self.setWindowTitle("Create New Road")
            self.b_delete.hide()
            defaults = self._get_default_road_values()
            self._apply_road_values(**defaults)
            return

        self._apply_road_values(
            name=self._road.name,
            orientation=self._road.orientation,
            position=self._road.position,
            number_of_forward_lanes=self._road.number_of_forward_lanes,
            number_of_backward_lanes=self._road.number_of_backward_lanes,
        )

    def accept(self) -> None:
        """
        Handle dialog acceptance by saving road changes.

        If editing an existing road, updates its properties. If creating
        a new road, adds it to the traffic model. Then closes the dialog.
        """
        name = self.t_name.text()
        orientation = RoadOrientation(self.d_orientation.currentIndex())
        position = self.s_position.value()
        forward_lanes = self.s_forward.value()
        backward_lanes = self.s_backward.value()

        try:
            if self._is_edit:
                self._application_controller.command_controller.update_road(
                    road=self._road,
                    name=name,
                    orientation=orientation,
                    position=position,
                    number_of_forward_lanes=forward_lanes,
                    number_of_backward_lanes=backward_lanes,
                )
            else:
                self._application_controller.command_controller.add_road(
                    name=name,
                    orientation=orientation,
                    position=position,
                    number_of_forward_lanes=forward_lanes,
                    number_of_backward_lanes=backward_lanes,
                )
        except (RoadValidationError, RoadTrafficSnapshotContextValidationError) as e:
            dialog = WarningDialog(
                "Validation Error",
                str(e),
                self,
            )
            dialog.exec()
            return
        else:
            self.parent().snackbar.show_message(
                f"Road '{name}' updated successfully." if self._is_edit else f"Road '{name}' created successfully.")

            super().accept()
