from typing import Callable

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import AtomNode
from pse.umlsl_editor.src.query.view import View


class HorizonComparisonNode(AtomNode):
    def __init__(self, latex_symbol: str, cmp: Callable[[float, float], bool], length: float):
        super().__init__(f"\\ell {latex_symbol} {length}")
        self._length = length
        self._cmp = cmp

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        return self._cmp(view.horizon.length(), self._length)


class HorizonCmpGreaterEqualsNode(HorizonComparisonNode):
    def __init__(self, length: float):
        super().__init__("\\geq", lambda x, y: x >= y, length)


class HorizonCmpGreaterNode(HorizonComparisonNode):
    def __init__(self, length: float):
        super().__init__(">", lambda x, y: x > y, length)


class HorizonCmpLessNode(HorizonComparisonNode):
    def __init__(self, length: float):
        super().__init__("<", lambda x, y: x < y, length)


class HorizonCmpLessEqualsNode(HorizonComparisonNode):
    def __init__(self, length: float):
        super().__init__("\\leq", lambda x, y: x <= y, length)
