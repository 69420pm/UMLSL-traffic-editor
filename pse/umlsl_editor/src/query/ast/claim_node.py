from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.query.ast.ast import View, AtomNode
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve


class ClaimNode(AtomNode):
    def __init__(self, car_resolve: CarResolve):
        super().__init__("cl")
        self._car_resolve = car_resolve

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1 or view.space_interval.length() <= 0:
            return False
        lane = view.seq_lanes[0]
        car_eval = self._car_resolve.resolve(variable_car_map)

        # 1) claim evaluates true if all segment in the lane are crossing segments
        reserved_crossings = car_eval.reserved_crossings
        if all(map(lambda s: s in reserved_crossings, lane.segments)):
            return True

        # 2)
        if len(lane.segments) != 1:
            return False
        target_segment = lane.segments[0]

        for segment_interval in car_eval.car_environment.path_segments_in_view(view):
            interval: Interval = segment_interval.interval
            segment: Segment = segment_interval.segment

            if segment == target_segment and view.space_interval.subset_of(list(interval)):
                return True

        return False
