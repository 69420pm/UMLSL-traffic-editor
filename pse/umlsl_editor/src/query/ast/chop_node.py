from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
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
        interesting_splits = []
        for physically_occupied_intervals in view.intersecting_cars.values():
            for segment, interval in physically_occupied_intervals.items():
                interesting_splits.extend([interval.start, interval.end])
        for reserved_intervals in view.reserved_segments.values():
            for segment, interval in reserved_intervals.items():
                interesting_splits.extend([interval.start, interval.end])
        for claimed_intervals in view.claimed_segments.values():
            for segment, interval in claimed_intervals.items():
                interesting_splits.extend([interval.start, interval.end])

        for split in interesting_splits:
            if self.evaluate_at_split(view, traffic_snapshot, variable_car_map, split):
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

        left_view, right_view = view.chop_horizontally(split_value)

        # if the left part is false, we can skip the computation of the right part
        left_eval = self._left.evaluate(traffic_snapshot, left_view, variable_car_map)
        if left_eval:
            right_eval = self._right.evaluate(traffic_snapshot, right_view, variable_car_map)
            if right_eval:
                return True

        return False

    def _format(self, left: str, right: str) -> str:
        return f"{left} \\frown {right}"


class VerticalChopNode(BinaryNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        super().__init__(Precedence.BINARY_CHOP, left, right)

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        seq_lanes = view.virtual_lanes

        for split_index in range(0, len(seq_lanes) + 1):
            lower_view, upper_view = view.chop_vertically(split_index)
            lower_eval = self._left.evaluate(traffic_snapshot, lower_view, variable_car_map)

            # if the lower part is false, we can skip the computation of the upper part
            if lower_eval:
                right_eval = self._right.evaluate(traffic_snapshot, upper_view, variable_car_map)

                if right_eval:
                    return True

        return False

    def _format(self, left: str, right: str) -> str:
        return f"_{{{left}}}^{{{right}}}"
