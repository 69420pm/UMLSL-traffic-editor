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

        # the list of reserved segments of the car
        car_reserved_segments: list[Segment] = []
        for reserved_lane in eval_car.environment.reserved_lanes:
            car_reserved_segments.append(reserved_lane.segment)
        for reserved_crossing in eval_car.environment.reserved_crossings:
            car_reserved_segments.append(reserved_crossing.segment)

        car_segment_intervals: list[SegmentInterval] = eval_car.environment.visible_segments_in_view(view)
        # maps each segment to its segment_interval
        car_segment_to_interval_map: dict[Segment, SegmentInterval] = dict()
        for car_segment_interval in car_segment_intervals:
            car_segment_to_interval_map[car_segment_interval.segment] = car_segment_interval

        lane_segments = view.virtual_lanes[0].segments
        space_intervals: list[Interval] = []
        virtual_pos = 0
        for segment in lane_segments:
            car_segment_interval = car_segment_to_interval_map.get(segment)
            if car_segment_interval is None:
                return False
            interval = car_segment_interval.interval

            # we need to ensure every segment of the lane is contained in a reserved segment interval of the car
            if car_segment_interval is None or segment not in car_reserved_segments:
                return False

            # we need to convert the relative position of the segment to its absolute position
            absolute_interval = Interval(
                virtual_pos + interval.start,
                virtual_pos + interval.end
            )
            space_intervals.append(absolute_interval)
            virtual_pos += interval.length()

        return view.space_interval.subset_of(Interval.union(space_intervals))