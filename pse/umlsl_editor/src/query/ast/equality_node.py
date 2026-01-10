from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import AtomNode
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve
from pse.umlsl_editor.src.query.view import View


class EqualityCarNode(AtomNode):
    def __init__(self, car_resolve1: CarResolve, car_resolve2: CarResolve):
        super().__init__(f"{car_resolve1.name} = {car_resolve2.name}")
        self._car_resolve1 = car_resolve1
        self._car_resolve2 = car_resolve2

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return self._car_resolve1.resolve(variable_car_map) is self._car_resolve2.resolve(variable_car_map)


class EqualityHorizonNode(AtomNode):
    def __init__(self, length: float):
        super().__init__(f"l = {length}")
        self._length = length

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return view.space_interval.length() == self._length
