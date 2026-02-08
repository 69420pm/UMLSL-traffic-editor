from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.traffic_value_objects.segments.car_environment import CarEnvironment
from pse.umlsl_editor.src.query.ast.ast import AtomNode, View


class CrossingSegmentNode(AtomNode):
    def __init__(self):
        super().__init__("cs")

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.space_interval.length() <= 0:
            return False

        # the definition in the paper is wrong when hchop/somewhere is involved
        # we therefore use the following definition:
        # TS, V, v |= cs <=> #L = 1 and |X| > 1 and forall (pi, X') in seg_path(ego): X' intersect X != empty => pi is CS
        # where seg_path splits the entire path into segments

        path_segment_intervals = view.car.environment.path_segment_intervals
        for path_segment_interval in path_segment_intervals:
            segment = path_segment_interval.segment
            interval = path_segment_interval.interval

            if interval.intersection(view.space_interval) is not None:
                # We found an intersection, check if segment is crossing segment.
                if segment.is_lane_segment:
                    return False

        print("evaluated true with ", view.space_interval)
        return True
