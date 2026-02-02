from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

from pse.umlsl_editor.src.view.ui.lists.models.car_list_model import CarModel
from pse.umlsl_editor.src.view.ui.lists.models.road_list_model import RoadListModel


class ViewModels:
    def __init__(self, application_controller: "ApplicationController") -> None:
        self.car_list_model = CarModel(application_controller=application_controller)
        self.road_list_model = RoadListModel(application_controller=application_controller)
        self.query_list_model = None

    def connect_signals(self, view_event_handler) -> None:
        self.car_list_model.connect_sinal(view_event_handler)
        self.road_list_model.connect_sinal(view_event_handler)
        # self.query_list_model.connect_sinal(view_event_handler)
