from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import AtomNode, View


class CrossingSegmentNode(AtomNode):
    def __init__(self):
        super().__init__("cs")

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.horizon.length() <= 0:
            return False

        for segment in view.virtual_lanes[0].segments_in_horizon(view.horizon, traffic_snapshot):
            if segment.is_lane_segment:
                return False

        return True
