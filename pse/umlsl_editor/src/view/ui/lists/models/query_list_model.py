from typing import TYPE_CHECKING
from urllib.parse import quote

from PySide6.QtCore import QModelIndex, Qt

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.query.evaluator import ParserError, UMLSLEvaluator
from pse.umlsl_editor.src.view.ui.lists.models.entity_list_model import EntityModel


class QueryListModel(EntityModel):
    QueryRole = EntityModel.NextRole
    IsValidRole = EntityModel.NextRole + 1
    EgoCarNameRole = EntityModel.NextRole + 2
    EgoCarColorRole = EntityModel.NextRole + 3
    LatexImageSourceRole = EntityModel.NextRole + 4

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
        ego_car = self._application_controller.data_controller.get_all_cars().get(query.assigned_car_uid)

        if role == QueryListModel.QueryRole:
            return str(query.latex)
        elif role == QueryListModel.IsValidRole:
            return bool(query.holding)
        elif role == QueryListModel.EgoCarNameRole:
            return str(ego_car.name) if ego_car else ""
        elif role == QueryListModel.EgoCarColorRole:
            return str(ego_car.color) if ego_car else ""
        elif role == QueryListModel.LatexImageSourceRole:
            # Convert the query's latex input to rendered LaTeX and create image URL
            try:
                evaluator = UMLSLEvaluator(
                    self._application_controller.get_traffic_snapshot_reader()
                )
                latex_code = evaluator.parse_ast(query.latex, ego_car).latex_code
                # URL-encode the latex string to safely pass it to the image provider
                encoded_latex = quote(latex_code, safe='')
                return f"image://latex/{encoded_latex}"
            except (ParserError, Exception):
                # If parsing fails, return empty string (no image)
                return ""

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
            QueryListModel.LatexImageSourceRole: b"role_latex_image",
        })
        return roles
