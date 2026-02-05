from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import AtomNode, View


class CrossingSegmentNode(AtomNode):
    def __init__(self):
        super().__init__("cs")

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.space_interval.length() <= 0:
            return False
        path = view.virtual_lanes[0]
        return all(map(lambda segment: not segment.is_lane_segment, path.segments))
