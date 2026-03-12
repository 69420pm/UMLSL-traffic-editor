from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.query.ast.ast import AtomNode, View


class FreeNode(AtomNode):
    def __init__(self):
        super().__init__("free")

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.horizon.length() <= 0:
            return False

        horizon = view.horizon
        horizon_reduction = 0.5001

        smaller_start = horizon.start + horizon_reduction
        smaller_end = max(smaller_start, horizon.end - horizon_reduction)
        smaller_horizon = Interval(smaller_start, smaller_end)
        smaller_view = View(view.virtual_lanes, smaller_horizon, view.car)

        return all(
            map(
                lambda car: len(car.environment.visible_segments_in_view(smaller_view)) == 0,
                traffic_snapshot.get_car_list()
            )
        )
