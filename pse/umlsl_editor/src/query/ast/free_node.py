from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.query.ast.ast import AtomNode, View


class FreeNode(AtomNode):
    def __init__(self):
        super().__init__("free")

    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        if len(view.virtual_lanes) != 1 or view.horizon.length() <= 0:
            return False

        horizon = view.horizon
        horizon_reduction = 0.001

        smaller_start = horizon.start + horizon_reduction
        smaller_end = max(smaller_start, horizon.end - horizon_reduction)
        smaller_horizon = Interval(smaller_start, smaller_end)

        for intersecting_car_uids, segment_intervals in view.get_visible_cars().items():
            for segment, interval in segment_intervals.items():
                if smaller_horizon.intersects(interval):
                    return False

        return True
