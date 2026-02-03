from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import View, AtomNode
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve
from pse.umlsl_editor.src.query.visible_segments import VisibleSegment


def is_claimed_segment(view: View, segment: Segment, car: Car) -> bool:
    segment_views: list[SegmentInterval] = VisibleSegment().compute_visible_segments(view, car)

    for segment_view in segment_views:
        if segment == segment_view.segment and segment_view.space_interval.subset_of(view.space_interval):
            return True

    return False


def is_claimed_crossing(segments: list[Segment], car: Car) -> bool:
    claimed_crossings = car.claimed_crossings
    return all(map(lambda segment: not segment.is_lane_segment and segment in claimed_crossings, segments))


def evaluate_claim(view: View, segments: list[Segment], car: Car):
    return (is_claimed_crossing(segments, car)
            or is_claimed_segment(view, segments[0], car))


class ClaimNode(AtomNode):
    def __init__(self, car_resolve: CarResolve):
        super().__init__("cl")
        self._car_resolve = car_resolve

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1 or view.space_interval.length() <= 0:
            return False
        path = view.seq_lanes[0]
        return evaluate_claim(view, path.segments, self._car_resolve.resolve(variable_car_map))
