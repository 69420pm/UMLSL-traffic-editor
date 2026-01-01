from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import UnaryNode, ASTNode, View


class ExistsNode(UnaryNode):
    def __init__(self, variable: str, child: ASTNode):
        super().__init__(child)
        self.variable = variable
        self.child = child

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if self.variable in variable_car_map:
            raise SyntaxError(f"Variable {self.variable} appears twice")

        for car in traffic_snapshot.get_cars():
            new_variable_map = variable_car_map.copy()
            new_variable_map[self.variable] = car

            if self.child.evaluate(traffic_snapshot, view, new_variable_map):
                return True

        return False


class ForAllNode(UnaryNode):
    def __init__(self, variable: str, child: ASTNode):
        super().__init__(child)
        self.variable = variable
        self.child = child

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if self.variable in variable_car_map:
            raise SyntaxError(f"Variable {self.variable} appears twice")

        for car in traffic_snapshot.get_cars():
            new_variable_map = variable_car_map.copy()
            new_variable_map[self.variable] = car

            if not self.child.evaluate(traffic_snapshot, view, new_variable_map):
                return False

        return True
