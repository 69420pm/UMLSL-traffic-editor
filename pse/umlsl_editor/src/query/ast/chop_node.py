from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.query.ast.ast import View, BinaryNode, Precedence, ASTNode

SMALLEST_STEP_SIZE = 0.5


class HorizontalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        horizon = view.horizon
        horizon_length = horizon.length()

        # we first iterate through interesting values of the horizon, i.e., the start and end positions of cars
        # for example, by doing so, hchop can be precisely used to detect collisions
        for car in traffic_snapshot.get_car_list():
            abs_intervals = car.environment.visible_segments_in_view_abs_intervals(view)
            for segment_interval in abs_intervals:
                interval = segment_interval.interval

                start, end = interval.start, interval.end
                if self.evaluate_at_split(view, traffic_snapshot, variable_car_map, start) \
                        or self.evaluate_at_split(view, traffic_snapshot, variable_car_map, end):
                    return True

        # if hchop did not succeed, we iterate through the horizon with exponentially decreasing step sizes
        level = 0
        while True:
            computed_step_size = 1.0 / (2 ** (1.5 * level + 1)) * horizon_length
            step_size = max(SMALLEST_STEP_SIZE, computed_step_size)

            if self.evaluate_with_step_size(view, traffic_snapshot, variable_car_map, step_size):
                return True

            if computed_step_size < SMALLEST_STEP_SIZE:
                return False

            level += 1


    def evaluate_with_step_size(self, view: View, traffic_snapshot: TrafficSnapshotModel,
                                variable_car_map: dict[str, Car], step_size: float):
        horizon = view.horizon
        split_value = view.horizon.start

        while split_value < horizon.end:
            if self.evaluate_at_split(view, traffic_snapshot, variable_car_map, split_value):
                return True
            split_value += step_size

        return False

    def evaluate_at_split(self, view: View, traffic_snapshot: TrafficSnapshotModel, variable_car_map: dict[str, Car],
                          split_value: float):
        horizon = view.horizon

        if not (horizon.start <= split_value <= horizon.end):
            return False

        left_horizon = Interval(horizon.start, split_value)
        left_view = View(view.virtual_lanes, left_horizon, view.car)
        left_eval = self._left.evaluate(traffic_snapshot, left_view, variable_car_map)

        # if the lhs is false, we can skip the computation of the rhs
        if left_eval:
            right_horizon = Interval(split_value, horizon.end)
            right_view = View(view.virtual_lanes, right_horizon, view.car)

            right_eval = self._right.evaluate(traffic_snapshot, right_view, variable_car_map)
            if right_eval:
                return True

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
