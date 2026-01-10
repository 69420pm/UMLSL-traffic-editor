from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import View, UnaryNode, BinaryNode, AtomNode, ASTNode


class TrueNode(AtomNode):
    def __init__(self):
        super().__init__("true")

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return True


class NegationNode(UnaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return not self.child.evaluate(traffic_snapshot, view, variable_car_map)

    def _format(self, child: str) -> str:
        return f"\\neg {child}"


class ConjunctionNode(BinaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return (self.left.evaluate(traffic_snapshot, view, variable_car_map)
                and self.right.evaluate(traffic_snapshot, view, variable_car_map))

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\land {right}"


class DisjunctionNode(BinaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return (self.left.evaluate(traffic_snapshot, view, variable_car_map)
                or self.right.evaluate(traffic_snapshot, view, variable_car_map))

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\lor {right}"
