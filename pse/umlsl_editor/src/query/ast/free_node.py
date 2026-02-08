from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import AtomNode, View


class FreeNode(AtomNode):
    def __init__(self):
        super().__init__("free")

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.space_interval.length() <= 0:
            return False

        return all(
            map(
                lambda car: len(car.environment.visible_segments_in_view(view)) == 0,
                traffic_snapshot.get_car_list()
            )
        )
