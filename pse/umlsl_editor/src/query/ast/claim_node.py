from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import View, NullaryNode
from pse.umlsl_editor.src.query.visible_segments import SegmentView, VisibleSegment


def is_claimed_segment(view: View, segment: Segment, car: Car) -> bool:
    segment_views: list[SegmentView] = VisibleSegment().compute_visible_segments(view, car)

    for segment_view in segment_views:
        if segment == segment_view.segment and segment_view.space_interval.subset_of(view.space_interval):
            return True

    return False


def is_claimed_crossing(traffic_snapshot: TrafficSnapshot, segments: list[Segment], car: Car) -> bool:
    car_context = traffic_snapshot.get_car_context(car)
    claimed_crossings = car_context.claimed_crossings
    return all(map(lambda segment: segment.is_crossing_segment() and segment in claimed_crossings, segments))


def evaluate_claim(traffic_snapshot: TrafficSnapshot, view: View, segments: list[Segment], car: Car):
    return (is_claimed_crossing(traffic_snapshot, segments, car)
            or is_claimed_segment(view, segments[0], car))


class ConstantClaimNode(NullaryNode):
    def __init__(self, car: Car):
        super().__init__()
        self.car = car

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1:
            return False
        path = view.seq_lanes[0]
        return evaluate_claim(traffic_snapshot, view, path.segments, self.car)


class VariableClaimNode(NullaryNode):
    def __init__(self, variable: str):
        super().__init__()
        self.variable = variable

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1:
            return False
        path = view.seq_lanes[0]
        car = variable_car_map[self.variable]
        return evaluate_claim(traffic_snapshot, view, path.segments, car)
