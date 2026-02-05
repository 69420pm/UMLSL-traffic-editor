from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import View, BinaryNode, Precedence, ASTNode
from pse.umlsl_editor.src.model.interval import Interval

# Sets the number of iterations for the horizontal chopping (at least 1). In each iteration, the new step_size is
# computed via step_size = prev_step_size / 2.
H_CHOP_EVAL_ITERATIONS = 5

class HorizontalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        for i in range(0, H_CHOP_EVAL_ITERATIONS - 1):
            if self.evaluate_with_step_size(i, traffic_snapshot, view, variable_car_map):
                return True

        return False

    def evaluate_with_step_size(self, eval_iteration: int, traffic_snapshot: TrafficSnapshotModel, view: View,
                                variable_car_map: dict[str, Car]):
        step_size = self.compute_step_size(eval_iteration)

        space_interval = view.space_interval
        split_value = space_interval.start

        iteration = 0
        while split_value < space_interval.end:
            if eval_iteration != 0 and self.skip_step(iteration):
                continue

            space_interval1 = Interval(space_interval.start, split_value)
            space_interval2 = Interval(split_value, space_interval.end)

            view1 = View(view.seq_lanes, space_interval1, view.car)
            view2 = View(view.seq_lanes, space_interval2, view.car)

            if (self._left.evaluate(traffic_snapshot, view1, variable_car_map)
                    and self._right.evaluate(traffic_snapshot, view2, variable_car_map)):
                return True

            split_value += step_size
            iteration += 1

    def compute_step_size(self, eval_iteration: int) -> float:
        # uses step_size: 1, 1/2, 1/4, 1/8, ...
        return 1.0 / pow(2, eval_iteration)

    def skip_step(self, iteration: int) -> bool:
        # skips every second step (already captured by the previous one because of our choice of 1/2^i)
        return iteration % 2 == 0

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\smallfrown {right}"


class VerticalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
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
