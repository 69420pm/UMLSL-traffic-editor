from dataclasses import dataclass

class LaneDirection:
    FORWARD = 1
    BACKWARD = -1

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

    def get_one_dimensional_position(self, traffic_snapshot_reader: 'TrafficSnapshotReader') -> float:
        road = traffic_snapshot_reader.get_road_by_uid(self.road_uid)
        lane_width = traffic_snapshot_reader.get_lane_width()
        if getattr(road.orientation, "name", None) == "HORIZONTAL":
            # Horizontal lanes: forward indices are lower y than backward indices.
            if self.lane_index >= 0:
                return road.position - self.lane_index * lane_width
            return road.position + (abs(self.lane_index)) * lane_width
        return road.position + self.lane_index * lane_width

    def get_name(self) -> str:
        return f"f{self.lane_index + 1}" if self.lane_index >= 0 else f"b{-self.lane_index}"

    def get_direction(self) -> int:
        return LaneDirection.FORWARD if self.lane_index >= 0 else LaneDirection.BACKWARD
