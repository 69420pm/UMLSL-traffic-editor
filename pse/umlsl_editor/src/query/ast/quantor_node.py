from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import UnaryNode, ASTNode, View


class ExistsNode(UnaryNode):
    def __init__(self, variable: str, child: ASTNode):
        super().__init__(child)
        self._variable = variable

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        # the AST parser guarantees that the variable is not already in the map
        for car in traffic_snapshot.get_cars():
            new_variable_map = variable_car_map.copy()
            new_variable_map[self._variable] = car

            if self._child.evaluate(traffic_snapshot, view, new_variable_map):
                return True

        return False

    def _format(self, child: str) -> str:
        return f"\\exists {self._variable}: {child}"

class ForallNode(UnaryNode):
    def __init__(self, variable: str, child: ASTNode):
        super().__init__(child)
        self._variable = variable

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        # the AST parser guarantees that the variable is not already in the map
        for car in traffic_snapshot.get_cars():
            new_variable_map = variable_car_map.copy()
            new_variable_map[self._variable] = car

            if not self._child.evaluate(traffic_snapshot, view, new_variable_map):
                return False

        return True

    def _format(self, child: str) -> str:
        return f"\\forall {self._variable}: {child}"
