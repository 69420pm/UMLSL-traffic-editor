from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.query.ast.ast import View, AtomNode
from pse.umlsl_editor.src.query.ast.car_resolve import CarResolve


class ClaimNode(AtomNode):
    def __init__(self, car_resolve: CarResolve):
        super().__init__(f"cl\\left({car_resolve.name}\\right)")
        self._car_resolve = car_resolve

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.horizon.length() <= 0:
            return False

        return True # todo
        segments: list[Segment] = view.virtual_lanes[0].segments_in_horizon(view.horizon, traffic_snapshot)
        car_eval = self._car_resolve.resolve(variable_car_map)

        # claim evaluates true if all segments (in the horizon) are crossing segments reserved by the (eval) car
        reserved_crossings = car_eval.environment.reserved_crossings
        if all(map(lambda s: s in reserved_crossings, segments)):
            return True

        # otherwise, we need to check whether the horizon is fully contained in the segment reserved by the (eval) car
        if len(segments) != 1:
            return False
        target_segment = segments[0]

        for segment_interval in car_eval.environment.visible_segments_in_view(view):
            interval: Interval = segment_interval.interval
            segment: Segment = segment_interval.segment

            if segment == target_segment and view.horizon.subset_of([interval]):
                return True

        return False
