from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QModelIndex, Slot

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.view.ui.lists.edit_road_dialog import EditRoadDialog
from pse.umlsl_editor.src.view.ui.lists.models.entity_list_model import EntityModel


class RoadListModel(EntityModel):
    NameRole = EntityModel.NextRole
    IconRole = EntityModel.NextRole + 1
    ValueRole = EntityModel.NextRole + 2

    def __init__(self, application_controller: "ApplicationController", parent=None):
        super().__init__(parent=parent)
        self._application_controller = application_controller

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        """Returns the data for a specific row and role."""
        parent_result = super().data(index, role)
        if parent_result is not None:
            return parent_result

        if not index.isValid():
            return None

        item = self._data[index.row()]
        is_vertical = item.orientation == RoadOrientation.VERTICAL

        if role == RoadListModel.NameRole:
            return str(item.name)
        elif role == RoadListModel.IconRole:
            return bool(is_vertical)
        elif role == RoadListModel.ValueRole:
            return ("x" if is_vertical else "y") + " = " + str(item.position)

        return None

    def roleNames(self):
        """Maps the integer Role IDs to variable names used in QML."""
        roles = super().roleNames()

        roles.update({
            RoadListModel.NameRole: b"role_name",
            RoadListModel.IconRole: b"role_isRotated",
            RoadListModel.ValueRole: b"role_value",
        })
        return roles

    @Slot(int)
    def handle_button_click(self, row):
        EditRoadDialog(self._data[row], application_controller=self._application_controller).exec_()
