from pse.umlsl_editor.src.core.entities.car import Car
from pse.umlsl_editor.src.core.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import NullaryNode, View
from pse.umlsl_editor.src.query.visible_segments import VisibleSegment


class FreeNode(NullaryNode):
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        return len(view.seq_lanes) == 1 and all(
            map(
                lambda car: len(VisibleSegment().compute_visible_segments(view, car)) == 0,
                traffic_snapshot.get_cars()
            )
        )
