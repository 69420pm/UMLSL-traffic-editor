from enum import Enum


class TurnDirection(Enum):
    LEFT = "left"
    RIGHT = "right"


class RoadOrientation(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class LaneDirection(Enum):
    FORWARD = "fn"
    BACKWARD = "bn"


class TurnIntent:
    """Encapsulates the 'Next Turn' logic tuple."""

    def __init__(self, direction: TurnDirection, target_lane_index: int):
        self.direction = direction
        self.target_lane_index = target_lane_index
