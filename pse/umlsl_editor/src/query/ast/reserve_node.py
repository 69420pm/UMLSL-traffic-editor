from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.query.ast.ast import View, AtomNode
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve


class ReserveNode(AtomNode):
    def __init__(self, car_resolve: CarResolve):
        super().__init__(f"re\\left({car_resolve.name}\\right)")
        self._car_resolve = car_resolve

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.space_interval.length() <= 0:
            return False

        # the car to evaluate the reserve node on
        eval_car = self._car_resolve.resolve(variable_car_map)
        reserved_lane_intervals: list[SegmentInterval] = eval_car.environment.reserved_lanes

        visible_segments: list[SegmentInterval] = eval_car.environment.path_segments_in_view(view)

        # check if all visible segments are reserved
        # if one of the segments is not reserved, the reserve node fails
        reserved_lanes: list[Segment] = list(map(lambda seg_interval: seg_interval.segment, reserved_lane_intervals))
        reserved_crossings: list[Segment] = eval_car.environment.reserved_crossings
        for visible_segment in visible_segments:
            if visible_segment.segment not in reserved_lanes and visible_segment.segment not in reserved_crossings:
                return False

        # compute intervals
        space_intervals: list[Interval] = []
        for visible_reserved_segment in visible_segments:
            interval = visible_reserved_segment.interval
            # we need to convert the relative position of the segment to its absolute position
            absolute_interval = Interval(
                visible_reserved_segment.virtual_pos + interval.start,
                visible_reserved_segment.virtual_pos + interval.end
            )
            space_intervals.append(absolute_interval)

        return view.space_interval.subset_of(Interval.union(space_intervals))
