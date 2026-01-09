from dataclasses import dataclass
from enum import Enum

from pse.umlsl_editor.src.model.entities.road import LaneDirection


class TurnDirection(Enum):
    """
    Enumeration representing
    the direction of a turn at an intersection.

    Attributes:
        LEFT: The car intends to turn left at the next intersection.
        RIGHT: The car intends to turn right at the next intersection.
    """

    LEFT = "left"
    RIGHT = "right"


class TurnIntentValidationError(ValueError):
    """
    Custom exception raised when a TurnIntent validation fails.
    """

    pass


@dataclass(frozen=True)
class TurnIntent:
    """
    Encapsulates the intended turn behavior at the next intersection.

    This dataclass represents the car's intention to turn at an upcoming
    intersection, specifying both the direction of the turn and the target
    lane the car wants to enter after completing the turn.

    Attributes:
        direction: The direction of the intended turn (LEFT or RIGHT).
        target_lane_index: The index of the target lane the car wants to enter after the turn.
        target_lane_direction: The direction of the target lane (FORWARD or BACKWARD).

    Raises:
        CarValidationError: If direction is not a TurnDirection or target_lane is not a Lane.
    """

    direction: TurnDirection

    target_lane_index: int
    target_lane_direction: LaneDirection

    def __post_init__(self) -> None:
        """
        Validates the TurnIntent instance after initialization.

        Performs the following validation checks:
        - direction must be a valid TurnDirection enum value
        - target_lane_index must be a positive integer
        - target_lane_direction must be a valid LaneDirection enum value

        Raises:
            TurnIntentValidationError: If any validation check fails.
        """
        raise NotImplementedError()
