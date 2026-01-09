from dataclasses import dataclass

from pse.umlsl_editor.src.model.entities.road import LaneDirection


@dataclass(frozen=True)
class Lane:
    """Represents a lane on a road, this is an immutable data structure and should act like a tuple.
    It's not a full entity as it doesn't have an identity beyond its road, index and direction."""
    road_name: str
    lane_index: int
    lane_direction: LaneDirection
