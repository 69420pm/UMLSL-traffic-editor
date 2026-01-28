from dataclasses import dataclass

from pse.umlsl_editor.src.model.entities.road import LaneDirection


@dataclass(frozen=True, kw_only=True)
class Lane:
    """Represents a lane on a road, this is an immutable data structure and should act like a tuple.
    It's not a full entity as it doesn't have an identity beyond its road, index and direction."""
    road_uid: str
    lane_index: int
    lane_direction: LaneDirection

    def __post_init__(self) -> None:
        """Validates the Lane instance after initialization.

        Performs the following validation checks:
        - road_uid must be a non-empty string
        - lane_index must be a non-negative integer larger than zero (because lane indices are 1-based)
        - lane_direction must be a valid LaneDirection enum value
        """
        if not isinstance(self.road_uid, str) or not self.road_uid:
            raise ValueError("road_uid must be a non-empty string")
        if not isinstance(self.lane_index, int) or self.lane_index < 1:
            raise ValueError("lane_index must be a positive integer")
        if not isinstance(self.lane_direction, LaneDirection):
            raise ValueError("lane_direction must be a LaneDirection")