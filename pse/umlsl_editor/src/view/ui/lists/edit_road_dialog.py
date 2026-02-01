from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_road_dialog import Ui_Edit_Road_Dialog


class EditRoadDialog(QDialog, Ui_Edit_Road_Dialog):
    def __init__(self, road: Road | None, application_controller: "ApplicationController", parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.road = road
        self.application_controller = application_controller

        if self.road is None:
            default_road_params = RoadParams(
                name="R",
                orientation=RoadOrientation.HORIZONTAL,
                position=0,
                number_of_forward_lanes=1,
                number_of_backward_lanes=1
            )
            self.road = Road.from_params(default_road_params)

        self.t_name.setText(self.road.name)

        self.d_orientation.clear()
        orientations = [orientation.name.lower() for orientation in RoadOrientation]
        self.d_orientation.addItems(orientations)
        self.d_orientation.setCurrentIndex(self.road.orientation.value)

        self.s_position.setValue(self.road.position)

        self.s_forward.setValue(self.road.number_of_forward_lanes)
        self.s_backward.setValue(self.road.number_of_backward_lanes)

    def accept(self) -> None:
        road_params = RoadParams(
            name=self.t_name.text(),
            orientation=RoadOrientation(self.d_orientation.currentIndex()),
            position=self.s_position.value(),
            number_of_forward_lanes=self.s_forward.value(),
            number_of_backward_lanes=self.s_backward.value()
        )
        self.application_controller.command_controller.upsert_road(road_uid=self.road.uid,
                                                                   road_params=road_params)
        super().accept()
