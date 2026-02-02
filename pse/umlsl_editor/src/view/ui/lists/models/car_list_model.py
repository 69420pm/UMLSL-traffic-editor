# pse/umlsl_editor/src/view/ui/lists/models/car_list_model.py
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QModelIndex, Slot

from pse.umlsl_editor.src.view.ui.lists.edit_car_dialog import EditCarDialog
from pse.umlsl_editor.src.view.ui.lists.models.entity_list_model import EntityModel

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController


class CarModel(EntityModel):
    # Start our roles after the parent's roles
    NameRole = EntityModel.NextRole + 0
    ColorRole = EntityModel.NextRole + 1
    ValueRole = EntityModel.NextRole + 2

    def __init__(self, application_controller: "ApplicationController", parent=None):
        # Pass the handler UP to the parent
        super().__init__(parent)
        self._application_controller = application_controller

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        # 1. Ask Parent (Handles IsSelectedRole)
        result = super().data(index, role)
        if result is not None:
            return result

        # 2. Handle Child Specifics
        item = self._data[index.row()]

        if role == CarModel.NameRole:
            return str(item.name)
        elif role == CarModel.ValueRole:
            return f"R: {item.lane.road_uid} L: {item.lane.lane_index}"
        elif role == CarModel.ColorRole:
            return str(item.color)

        return None

    def roleNames(self):
        # 1. Get Parent Roles (includes "role_is_selected")
        roles = super().roleNames()

        # 2. Add Child Roles
        roles.update({
            CarModel.NameRole: b"role_name",
            CarModel.ColorRole: b"role_color",
            CarModel.ValueRole: b"role_value",
        })
        return roles

    @Slot(int)
    def handle_button_click(self, row):
        EditCarDialog(self._data[row], application_controller=self._application_controller).exec_()
