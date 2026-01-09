from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import NullaryNode
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve
from pse.umlsl_editor.src.query.view import View

class EqualityCarNode(NullaryNode):
    def __init__(self, car_resolve1: CarResolve, car_resolve2: CarResolve):
        super().__init__()
        self.car_resolve1 = car_resolve1
        self.car_resolve2 = car_resolve2

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return self.car_resolve1.resolve(variable_car_map) is self.car_resolve2.resolve(variable_car_map)


class EqualityHorizonNode(NullaryNode):
    def __init__(self, length: float):
        super().__init__()
        self.length = length

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        # todo: wrong
        return view.space_interval.length() == self.length
