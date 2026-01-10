from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import UnaryNode, ASTNode, View


class ExistsNode(UnaryNode):
    def __init__(self, variable: str, child: ASTNode):
        super().__init__(child)
        self.variable = variable

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        # the AST parser guarantees that the variable is not already in the map
        for car in traffic_snapshot.get_cars():
            new_variable_map = variable_car_map.copy()
            new_variable_map[self.variable] = car

            if self.child.evaluate(traffic_snapshot, view, new_variable_map):
                return True

        return False

    def _format(self, child: str) -> str:
        return f"\\exists {self.variable}: {child}"

class ForallNode(UnaryNode):
    def __init__(self, variable: str, child: ASTNode):
        super().__init__(child)
        self.variable = variable

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        # the AST parser guarantees that the variable is not already in the map
        for car in traffic_snapshot.get_cars():
            new_variable_map = variable_car_map.copy()
            new_variable_map[self.variable] = car

            if not self.child.evaluate(traffic_snapshot, view, new_variable_map):
                return False

        return True

    def _format(self, child: str) -> str:
        return f"\\forall {self.variable}: {child}"
