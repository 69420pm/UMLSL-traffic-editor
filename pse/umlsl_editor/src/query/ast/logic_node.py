from pse.umlsl_editor.src.core.entities.car import Car
from pse.umlsl_editor.src.core.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import View, UnaryNode, BinaryNode, NullaryNode


class TrueNode(NullaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return True


class NegationNode(UnaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return not self.child.evaluate(traffic_snapshot, view, variable_car_map)


class ConjunctionNode(BinaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return (self.left.evaluate(traffic_snapshot, view, variable_car_map)
                and self.right.evaluate(traffic_snapshot, view, variable_car_map))


class DisjunctionNode(BinaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return (self.left.evaluate(traffic_snapshot, view, variable_car_map)
                or self.right.evaluate(traffic_snapshot, view, variable_car_map))
