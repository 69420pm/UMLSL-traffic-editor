from dataclasses import dataclass

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Path
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent


@dataclass
class CarEnvironment:
    path_pursuit: Path
    virtual_lanes: list[Path]

    @staticmethod
    def create_virtual_lanes(
            traffic_snapshot: TrafficSnapshotReader,
            lane: LaneSegment,
            turn_intent: TurnIntent
    ) -> 'CarEnvironment':
        road_id = lane.lane.road_uid
        road = traffic_snapshot.get_road_by_uid(road_id)

        # todo
        pass
