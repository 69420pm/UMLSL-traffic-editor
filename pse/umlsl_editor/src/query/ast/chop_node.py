from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import View, BinaryNode, Precedence, ASTNode
from pse.umlsl_editor.src.query.interval import Interval

# Determines in how many pieces we split a given space interval
H_CHOP_ACCURACY: float = 1000.0


class HorizontalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        space_interval = view.space_interval
        step_size = space_interval.length() / H_CHOP_ACCURACY

        split_value = space_interval.start
        while split_value < space_interval.end:
            space_interval1 = Interval(space_interval.start, split_value)
            space_interval2 = Interval(split_value, space_interval.end)

            view1 = View(view.seq_lanes, space_interval1, view.car)
            view2 = View(view.seq_lanes, space_interval2, view.car)

            if (self._left.evaluate(traffic_snapshot, view1, variable_car_map)
                    and self._right.evaluate(traffic_snapshot, view2, variable_car_map)):
                return True

            split_value += step_size

        return False

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\smallfrown {right}"


class VerticalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        seq_lanes = view.seq_lanes

        for split_index in range(0, len(seq_lanes) + 1):
            smaller = seq_lanes[:split_index]  # take all lanes whose index is < split_index
            bigger = seq_lanes[split_index:]

            view1 = View(smaller, view.space_interval, view.car)
            view2 = View(bigger, view.space_interval, view.car)

            if (self._left.evaluate(traffic_snapshot, view1, variable_car_map)
                    and self._right.evaluate(traffic_snapshot, view2, variable_car_map)):
                return True

        return False

    def _format(self, left: str, right: str) -> str:
        return f"_{left}^{right}"
