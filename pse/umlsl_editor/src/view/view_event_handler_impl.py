from pse.umlsl_editor.src.controllers.view_event_contract import ViewEventHandler
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.entity import Entity
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.view.view_models import ViewModelContainer


class ViewEventHandlerImplementation(ViewEventHandler):
    def __init__(self):
        self.view_models = ViewModelContainer()

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

    def add_crossing_segment_view(self, crossing_segment: CrossingSegment) -> None:
        pass

    def remove_crossing_segment_view(self, crossing_segment: CrossingSegment) -> None:
        pass

    def update_crossing_segment_view(self, crossing_segment: CrossingSegment) -> None:
        pass

    def add_query_view(self, query: UMLSLQuery) -> None:
        self.view_models.umlsl_query_list_model.add_query(query)

    def remove_query_view(self, query: UMLSLQuery) -> None:
        self.view_models.umlsl_query_list_model.remove_query(query)

    def update_query_view(self, query: UMLSLQuery) -> None:
        self.view_models.umlsl_query_list_model.update_query(query)

    def change_breaking_acceleration(self, breaking_acceleration: float) -> None:
        pass

    def toggle_coordinate_system(self, render_coordinate_system: bool) -> None:
        pass

    def toggle_safety_distance(self, render_safety_distance: bool) -> None:
        pass

    def select_entity_view(self, entity: Entity) -> None:
        pass

    def deselect_entity_view(self, entity: Entity) -> None:
        pass

    def clear_selection_view(self) -> None:
        pass