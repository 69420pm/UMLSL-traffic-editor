from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import AtomNode, Precedence
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve
from pse.umlsl_editor.src.query.view import View


class CarEqualityNode(AtomNode):
    def __init__(self, car_resolve1: CarResolve, car_resolve2: CarResolve):
        super().__init__(f"{car_resolve1.name} = {car_resolve2.name}")
        self._car_resolve1 = car_resolve1
        self._car_resolve2 = car_resolve2
        self._precedence = Precedence.UNARY_EQUALITY

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        return self._car_resolve1.resolve(variable_car_map) is self._car_resolve2.resolve(variable_car_map)


class CarNotEqualsNode(AtomNode):
    def __init__(self, car_resolve1: CarResolve, car_resolve2: CarResolve):
        super().__init__(f"{car_resolve1.name} \\neq {car_resolve2.name}")
        self._car_resolve1 = car_resolve1
        self._car_resolve2 = car_resolve2
        self._precedence = Precedence.UNARY_EQUALITY

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        return not (self._car_resolve1.resolve(variable_car_map) is self._car_resolve2.resolve(variable_car_map))
