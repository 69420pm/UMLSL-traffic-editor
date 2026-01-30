from dataclasses import dataclass

@dataclass(frozen=True, kw_only=True)
class Lane:
    """Represents a lane on a road, this is an immutable data structure and should act like a tuple.
    It's not a full entity as it doesn't have an identity beyond its road, index and direction."""
    road_uid: str
    lane_index: int
    """The index of the lane, the inner most forward lane has index 0 and the inner most backward lane has index -1"""

    def __post_init__(self) -> None:
        """Validates the Lane instance after initialization.

        Performs the following validation checks:
        - road_uid must be a non-empty string
        - lane_index must be a  integer
        """
        if not isinstance(self.road_uid, str) or not self.road_uid:
            raise ValueError("road_uid must be a non-empty string")
        if not isinstance(self.lane_index, int) :
            raise ValueError("lane_index must be a integer")
