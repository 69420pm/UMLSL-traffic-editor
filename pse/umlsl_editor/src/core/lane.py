from dataclasses import dataclass
from enum import Enum


class LaneDirection(Enum):
    FORWARD = "fn"
    BACKWARD = "bn"


@dataclass
class Lane:
    """Represents a specific lane on a road. Every lane must belong to a road."""

    index: int
    """The index of the lane on the road (1-based) counted from the inside out"""

    direction: LaneDirection
    """The direction of traffic flow in this lane."""
