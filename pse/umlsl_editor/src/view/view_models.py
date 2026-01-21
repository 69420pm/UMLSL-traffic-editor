from typing import List

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from pse.umlsl_editor.src.model.entities.entity import Entity
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.view.entity_list_model import EntityListModel


class ViewModel:
    def __init__(self):
        self.car_list_model = EntityListModel()
        self.road_list_model = EntityListModel()
        self.umlsl_query_list_model = EntityListModel()
