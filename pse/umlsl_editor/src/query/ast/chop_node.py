from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import View, BinaryNode, Precedence, ASTNode
from pse.umlsl_editor.src.model.interval import Interval

# Sets the number of iterations for the horizontal chopping (at least 1). In each iteration, the new step_size is
# computed via step_size = prev_step_size / 2.
H_CHOP_EVAL_ITERATIONS = 4

class HorizontalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        # todo: split pieces in half on every iteration
        step_size = 0.5  # self.compute_step_size(eval_iteration)
        iteration = 0

        split_value = view.horizon.start
        space_interval = view.horizon
        while split_value < space_interval.end - 0.001:
            left_horizon = Interval(space_interval.start, split_value)
            left_view = View(view.virtual_lanes, left_horizon, view.car)
            left = self._left.evaluate(traffic_snapshot, left_view, variable_car_map)

            # if the lhs is false, we can skip the computation of the rhs
            if left:
                right_horizon = Interval(split_value, space_interval.end)
                right_view = View(view.virtual_lanes, right_horizon, view.car)

                right = self._right.evaluate(traffic_snapshot, right_view, variable_car_map)
                if right:
                    return True

            split_value += step_size

        return False

    def compute_step_size(self, eval_iteration: int) -> float:
        # uses step_size: 1, 1/2, 1/4, 1/8, ...
        return 1.0 / pow(2, eval_iteration)

    def skip_step(self, iteration: int) -> bool:
        # skips every second step (already captured by the previous one because of our choice of 1/2^i)
        return iteration % 2 == 0

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\frown {right}"


class VerticalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        seq_lanes = view.virtual_lanes

        for split_index in range(0, len(seq_lanes) + 1):
            lower_lanes = seq_lanes[:split_index]  # take all lanes whose index is < split_index
            lower_view = View(lower_lanes, view.horizon, view.car)
            lower_eval = self._left.evaluate(traffic_snapshot, lower_view, variable_car_map)

            # if the lower part is false, we can skip the computation of the upper part
            if lower_eval:
                upper_lanes = seq_lanes[split_index:]
                upper_view = View(upper_lanes, view.horizon, view.car)
                right_eval = self._right.evaluate(traffic_snapshot, upper_view, variable_car_map)

                if right_eval:
                    return True

        return False

    def _format(self, left: str, right: str) -> str:
        return f"_{{{left}}}^{{{right}}}"
