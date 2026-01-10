from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import AtomNode, View
from pse.umlsl_editor.src.query.visible_segments import VisibleSegment


class FreeNode(AtomNode):
    def __init__(self):
        super().__init__("free")

    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.seq_lanes) != 1 or view.space_interval.length() <= 0:
            return False
        return all(
            map(
                lambda car: len(VisibleSegment().compute_visible_segments(view, car)) == 0,
                traffic_snapshot.get_cars()
            )
        )
