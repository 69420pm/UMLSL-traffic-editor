from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, Qt

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.view.ui.lists.models.entity_list_model import EntityModel


class QueryListModel(EntityModel):
    QueryRole = EntityModel.NextRole
    IsValidRole = EntityModel.NextRole + 1
    EgoCarNameRole = EntityModel.NextRole + 2
    EgoCarColorRole = EntityModel.NextRole + 3

    def __init__(
            self,
            application_controller: "ApplicationController",
            parent=None,
    ) -> None:

        super().__init__(parent=parent)
        self._application_controller = application_controller

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):

        parent_result = super().data(index, role)
        if parent_result is not None:
            return parent_result

        if not index.isValid():
            return None

        query = self._data[index.row()]
        ego_car = self._application_controller.data_controller.get_all_cars()[query.assigned_car_uid]

        if role == QueryListModel.QueryRole:
            return str(query.latex)
        elif role == QueryListModel.IsValidRole:
            return bool(query.validation)
        elif role == QueryListModel.EgoCarNameRole:
            return str(ego_car.name)
        elif role == QueryListModel.EgoCarColorRole:
            return str(ego_car.color)

        return None

    def roleNames(self) -> dict[int, bytes]:
        """
        Return the mapping of role IDs to QML role names.

        Extends the parent class roles with road-specific roles.

        Returns:
            Dictionary mapping role constants to QML property names.
        """
        roles = super().roleNames()
        roles.update({
            QueryListModel.QueryRole: b"role_query",
            QueryListModel.IsValidRole: b"role_valid",
            QueryListModel.EgoCarNameRole: b"role_ego_name",
            QueryListModel.EgoCarColorRole: b"role_ego_color",
        })
        return roles
