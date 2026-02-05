"""
Edit road dialog for the UMLSL Traffic Editor.

Provides a dialog for creating new roads or editing existing road properties
such as name, orientation, position, and lane counts.
"""

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.model.errors.road_errors import (
    RoadTrafficSnapshotContextValidationError,
    RoadValidationError,
)
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
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

        if not self._is_edit:
            self._road = self._create_default_road()

        self._populate_fields()

    def _create_default_road(self) -> Road:
        """
        Create a new road with default parameter values.

        Returns:
            A new Road instance with default configuration.
        """
        default_params = RoadParams(
            name="",
            orientation=RoadOrientation.HORIZONTAL,
            position=0,
            number_of_forward_lanes=1,
            number_of_backward_lanes=1,
        )
        return Road.from_params(default_params)

    def _populate_fields(self) -> None:
        """Populate dialog fields with the current road's values."""
        self.t_name.setText(self._road.name)

        self.d_orientation.clear()
        orientations = [orientation.name.lower() for orientation in RoadOrientation]
        self.d_orientation.addItems(orientations)
        self.d_orientation.setCurrentIndex(self._road.orientation.value)

        self.s_position.setValue(self._road.position)
        self.s_forward.setValue(self._road.number_of_forward_lanes)
        self.s_backward.setValue(self._road.number_of_backward_lanes)

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

        super().accept()
