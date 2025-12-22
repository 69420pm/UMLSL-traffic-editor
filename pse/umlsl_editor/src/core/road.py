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
    """Unique human-readable name of the road. Acs as an unique identifier."""

    orientation: RoadOrientation
    """Orientation of the road (e.g., horizontal, vertical)."""

    position: float
    """Position of the road in the coordinate system."""

    lanes: Dict[str, Lane] = field(default_factory=dict)
    """Dictionary of lanes indexed by lane ID."""

    def get_lane_by_id(self, lane: str) -> Optional[Lane]:
        """
        Retrieve a lane by its identifier.

        Args:
            lane: The unique identifier of the lane to retrieve

        Returns:
            The Lane object if found, None otherwise
        """
        pass
