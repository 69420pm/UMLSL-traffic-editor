from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import View, AtomNode
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve
from pse.umlsl_editor.src.query.visible_segments import SegmentView, VisibleSegment


def segment_reserved(view: View, segment: Segment, car: Car) -> bool:
    if segment not in car.reserved_lanes and segment not in car.reserved_crossings:
        return False

    segment_views: list[SegmentView] = VisibleSegment().compute_visible_segments(view, car)
    # todo: missing space interval check
    return any(map(lambda segment_view: segment == segment_view.segment, segment_views))


def evaluate_reserve(view: View, segments: list[Segment], car: Car):
    return all(map(lambda segment: segment_reserved(view, segment, car), segments))


class ReserveNode(AtomNode):
    def __init__(self, car_resolve: CarResolve):
        super().__init__("re")
        self._car_resolve = car_resolve

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1 or view.space_interval.length() <= 0:
            return False
        path = view.seq_lanes[0]
        
        car = view.car
        lane = view.seq_lanes[0]

        # todo: not quite right i think
        visible_segments: list[SegmentView] = VisibleSegment().compute_visible_segments(view, car)
        segment_to_segment_views: dict[Segment, list[SegmentView]] = {}
        for segment_view in visible_segments:
            if segment_view.segment not in segment_to_segment_views:
                segment_to_segment_views[segment_view.segment] = []
            segment_to_segment_views[segment_view.segment].append(segment_view)
        
        for segment in lane.segments:
            # each segment must be reserved
            if segment not in car.reserved_lanes or segment not in car.reserved_crossings:
                return False

            # each segment must be visible
            if segment not in segment_to_segment_views:
                return False

            # todo: if not (view.space_interval subset of (union of

        return evaluate_reserve(view, path.segments, self._car_resolve.resolve(variable_car_map))
