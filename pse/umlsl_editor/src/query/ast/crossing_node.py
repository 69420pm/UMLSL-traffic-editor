from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot, CrossingSegment
from pse.umlsl_editor.src.query.ast.ast import NullaryNode, View


class CrossingSegmentNode(NullaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1:
            return False
        path = view.seq_lanes[0]
        return all(map(lambda segment: segment is CrossingSegment, path.segments))
