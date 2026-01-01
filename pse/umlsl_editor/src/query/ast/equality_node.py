from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import NullaryNode
from pse.umlsl_editor.src.query.view import View


class EqualityCarNode(NullaryNode):
    def __init__(self, car_variable1: str, car_variable2: str):
        super().__init__()
        self.car_variable1 = car_variable1
        self.car_variable2 = car_variable2

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return variable_car_map[self.car_variable1] == variable_car_map[self.car_variable2]


class EqualityHorizonNode(NullaryNode):
    def __init(self, length: float):
        self.length = length

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return view.space_interval.length() == self.length
