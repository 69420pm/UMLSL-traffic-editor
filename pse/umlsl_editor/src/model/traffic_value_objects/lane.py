from dataclasses import dataclass

from pse.umlsl_editor.src.model.entities.entity import Entity


@dataclass(kw_only=True)
class Lane:
    """Represents a lane on a road, this is an immutable data structure and should act like a tuple.
    It's not a full entity as it doesn't have an identity beyond its road, index and direction."""
    lane_index: int
    """The index of the lane, the inner most forward lane has index 0 and the inner most backward lane has index -1"""
    road_uid: str

    def __post_init__(self) -> None:
        """Validates the Lane instance after initialization.

        Performs the following validation checks:
        - lane_index must be an integer
        - road_uid must be a string
        """
        if not isinstance(self.road_uid, int):
            raise ValueError("road_uid must be a string")

        if not isinstance(self.lane_index, int) :
            raise ValueError("lane_index must be a integer")
