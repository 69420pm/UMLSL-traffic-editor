from typing import List

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.view.ui.lists.models.CarModel import CarModel
from pse.umlsl_editor.src.view.ui.lists.models.RoadModel import RoadModel


class ViewModels:
    def __init__(self, roads: List[Road] | None, cars: List[Car] | None, umlsl_queries: List[UMLSLQuery] | None) -> None:
        self.car_list_model = CarModel(cars)
        self.road_list_model = RoadModel(roads)
        self.query_list_model = None
