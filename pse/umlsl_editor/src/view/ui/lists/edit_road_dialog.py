from PySide6.QtWidgets import QDialog

from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.view.widgets.compiled_widgets.ui_road_dialog import Ui_Edit_Road_Dialog


class EditRoadDialog(QDialog, Ui_Edit_Road_Dialog):
    def __init__(self, road:Road, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        self.road = road


        self.t_name.setText(self.road.name)

        self.d_orientation.clear()
        orientations = [orientation.value for orientation in RoadOrientation]
        self.d_orientation.addItems(orientations)
        self.d_orientation.setCurrentIndex(0 if self.road.orientation == RoadOrientation.HORIZONTAL else 1)

        self.s_position.setValue(road.position)

        self.s_forward.setValue(road.forward_lanes)
        self.s_backward.setValue(road.backward_lanes)
