import typing

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import View, UnaryNode, BinaryNode, AtomNode, ASTNode, Precedence

if typing.TYPE_CHECKING:
    from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel


class TrueNode(AtomNode):
    def __init__(self):
        super().__init__("true")

    def evaluate(self, traffic_snapshot: "TrafficSnapshotModel", view: View, variable_car_map: dict[str, Car]) -> bool:
        return True


class NegationNode(UnaryNode):
    def evaluate(self, traffic_snapshot: "TrafficSnapshotModel", view: View, variable_car_map: dict[str, Car]) -> bool:
        return not self._child.evaluate(traffic_snapshot, view, variable_car_map)

    def _format(self, child: str) -> str:
        return f"\\neg {child}"


class ConjunctionNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CONJUNCTION, left, right)

    def evaluate(self, traffic_snapshot: "TrafficSnapshotModel", view: View, variable_car_map: dict[str, Car]) -> bool:
        return (self._left.evaluate(traffic_snapshot, view, variable_car_map)
                and self._right.evaluate(traffic_snapshot, view, variable_car_map))

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\wedge {right}"


class DisjunctionNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_DISJUNCTION, left, right)

    def evaluate(self, traffic_snapshot: "TrafficSnapshotModel", view: View, variable_car_map: dict[str, Car]) -> bool:
        return (self._left.evaluate(traffic_snapshot, view, variable_car_map)
                or self._right.evaluate(traffic_snapshot, view, variable_car_map))

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\vee {right}"


class ImpliesNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_DISJUNCTION, left, right)

    def evaluate(self, traffic_snapshot: "TrafficSnapshotModel", view: View, variable_car_map: dict[str, Car]) -> bool:
        return (not self._left.evaluate(traffic_snapshot, view, variable_car_map)
                or self._right.evaluate(traffic_snapshot, view, variable_car_map))

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\Longrightarrow {right}"
