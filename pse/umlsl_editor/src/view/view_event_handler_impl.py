from PySide6.QtCore import Signal
from PySide6.QtCore import SignalInstance

from pse.umlsl_editor.src.controllers.view_event_contract import ViewEventHandler
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.view.view_models import ViewModels


class ViewEventHandlerImplementation(ViewEventHandler):
    selection_changed = Signal(str)
    toggle_coordinate_system_signal = Signal(bool)
    toggle_grid_signal = Signal(bool)
    toggle_safety_distance_signal = Signal(bool)

    def get_on_selection_changed_signal(self) -> "SignalInstance":
        return self.selection_changed

    def get_on_toggle_coordinate_system_signal(self) -> "SignalInstance":
        return self.toggle_coordinate_system_signal

    def get_on_toggle_grid_signal(self) -> "SignalInstance":
        return self.toggle_grid_signal

    def get_on_toggle_safety_distance_signal(self) -> "SignalInstance":
        return self.toggle_safety_distance_signal

    def __init__(self, view_model: ViewModels):
        super().__init__()
        self.view_models = view_model
        self.current_selected_uid: str = ""
        self.should_render_coordinate_system: bool = True
        self.should_render_grid: bool = True
        self.should_render_safety_distance: bool = True

    def add_car_view(self, car: Car) -> None:
        self.view_models.car_list_model.add_entity(car)

    def remove_car_view(self, car: Car) -> None:
        self.view_models.car_list_model.remove_entity(car)

    def update_car_view(self, car: Car) -> None:
        self.view_models.car_list_model.update_entity(car)

    def add_road_view(self, road: Road) -> None:
        self.view_models.road_list_model.add_entity(road)

    def remove_road_view(self, road: Road) -> None:
        self.view_models.road_list_model.remove_entity(road)

    def update_road_view(self, road: Road) -> None:
        self.view_models.road_list_model.update_entity(road)

    def add_query_view(self, query: UMLSLQuery) -> None:
        self.view_models.query_list_model.add_entity(query)

    def remove_query_view(self, query: UMLSLQuery) -> None:
        self.view_models.query_list_model.remove_entity(query)

    def update_query_view(self, query: UMLSLQuery) -> None:
        self.view_models.query_list_model.update_entity(query)

    def set_coordinate_system(self, render_coordinate_system: bool) -> None:
        self.should_render_coordinate_system = render_coordinate_system
        self.toggle_coordinate_system_signal.emit(render_coordinate_system)

    def set_grid(self, render_grid: bool) -> None:
        self.should_render_grid = render_grid
        self.toggle_grid_signal.emit(render_grid)

    def set_safety_distance(self, render_safety_distance: bool) -> None:
        self.should_render_safety_distance = render_safety_distance
        self.toggle_safety_distance_signal.emit(render_safety_distance)

    def get_current_selected_uid(self) -> str:
        return self.current_selected_uid

    def entity_selected_view(self, uid: str) -> None:
        if uid != self.current_selected_uid:
            self.current_selected_uid = uid
        else:
            self.current_selected_uid = ""

        self.selection_changed.emit(self.current_selected_uid)
