from dataclasses import dataclass

import pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader


@dataclass(frozen=True, kw_only=True)
class Lane:
    """Represents a lane on a road, this is an immutable data structure and should act like a tuple.
    It's not a full entity as it doesn't have an identity beyond its road, index and direction."""
    lane_index: int
    """The index of the lane, the inner most forward lane has index 0 and the inner most backward lane has index -1"""
    road_uid: str
    """The uid of the road this lane belongs to"""

    def __post_init__(self) -> None:
        """Validates the Lane instance after initialization.

        Performs the following validation checks:
        - lane_index must be an integer
        - road_uid must be a string
        """
        if not isinstance(self.road_uid, str):
            raise ValueError("road_uid must be a string")

        if not isinstance(self.lane_index, int):
            raise ValueError("lane_index must be a integer")

    def get_one_dimensional_position(self,
                                     traffic_snapshot_reader: pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader.TrafficSnapshotReader) -> float:

        road = traffic_snapshot_reader.get_road_by_uid(self.road_uid)
        return road.position + self.lane_index * traffic_snapshot_reader.get_lane_width()
