from pse.umlsl_editor.src.core.entities.car import Car
from pse.umlsl_editor.src.core.view_models.traffic_snapshot import TrafficSnapshot, Segment
from pse.umlsl_editor.src.query.ast.ast import View, NullaryNode
from pse.umlsl_editor.src.query.visible_segments import SegmentView, VisibleSegment


def segment_reserved(traffic_snapshot: TrafficSnapshot, view: View, segment: Segment, car: Car) -> bool:
    car_context = traffic_snapshot.get_car_context(car)
    if segment not in car_context.reserved_lanes and segment not in car_context.reserved_crossings:
        return False

    segment_views: list[SegmentView] = VisibleSegment().compute_visible_segments(view, car)
    # todo: missing space interval check
    return any(map(lambda segment_view: segment == segment_view.segment, segment_views))


def evaluate_reserve(traffic_snapshot: TrafficSnapshot, view: View, segments: list[Segment], car: Car):
    return all(map(lambda segment: segment_reserved(traffic_snapshot, view, segment, car), segments))


class ConstantReserveNode(NullaryNode):
    def __init__(self, car: Car):
        super().__init__()
        self.car = car

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1:
            return False
        path = view.seq_lanes[0]
        return evaluate_reserve(traffic_snapshot, view, path.segments, self.car)


class VariableReserveNode(NullaryNode):
    def __init__(self, variable: str):
        super().__init__()
        self.variable = variable

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1:
            return False
        path = view.seq_lanes[0]
        car = variable_car_map[self.variable]
        return evaluate_reserve(traffic_snapshot, view, path.segments, car)
