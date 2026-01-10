from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import NullaryNode, View


class CrossingSegmentNode(NullaryNode):
    def __init__(self):
        super().__init__("cs")

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1:
            return False
        path = view.seq_lanes[0]
        return all(map(lambda segment: not segment.is_lane_segment, path.segments))
