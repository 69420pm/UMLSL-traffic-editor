from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.commands.roads.edit_road import EditRoad

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_road_dialog import Ui_Edit_Road_Dialog


class EditRoadDialog(QDialog, Ui_Edit_Road_Dialog):
    def __init__(self, road:Road, application_controller:"ApplicationController", parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.road = road
        self.application_controller = application_controller

        self.t_name.setText(self.road.name)

        self.d_orientation.clear()
        orientations = [orientation.name.lower() for orientation in RoadOrientation]
        self.d_orientation.addItems(orientations)
        self.d_orientation.setCurrentIndex(road.orientation.value)

        self.s_position.setValue(road.position)

        self.s_forward.setValue(road.forward_lanes)
        self.s_backward.setValue(road.backward_lanes)

    def accept(self) -> None:
        road_params = RoadParams(
            name=self.t_name.text(),
            orientation=RoadOrientation[self.d_orientation.currentIndex()],
            position=self.s_position.value(),
            forward_lanes=self.s_forward.value(),
            backward_lanes=self.s_backward.value(),
        )

        self.application_controller.command_controller.execute_command(EditRoad(road_params=road_params,
                                                         traffic_snapshot_reader=self.application_controller.get_traffic_snapshot_reader(),
                                                         traffic_snapshot_writer=self.application_controller.get_traffic_snapshot_writer(),
                                                         ))
        super().accept()
