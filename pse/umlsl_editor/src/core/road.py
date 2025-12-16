from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional

from pse.umlsl_editor.src.core.lane import Lane


class RoadOrientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class Road:
    """
    Represents a road in the traffic simulation system.
    """

    name: str
    """Human-readable name of the road."""

    orientation: RoadOrientation
    """Orientation of the road (e.g., horizontal, vertical)."""

    position: float
    """Position of the road in the coordinate system."""

    lanes: Dict[str, Lane] = field(default_factory=dict)
    """Dictionary of lanes indexed by lane ID."""

    id: str = field(default="", init=False)
    """Unique identifier for the road."""

    def get_lane_by_id(self, lane_id: str) -> Optional[Lane]:
        """
        Retrieve a lane by its identifier.

        Args:
            lane_id: The unique identifier of the lane to retrieve

        Returns:
            The Lane object if found, None otherwise
        """
        pass
