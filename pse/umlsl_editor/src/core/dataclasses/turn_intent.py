import json
from dataclasses import dataclass
from enum import Enum
from typing import Any

from pse.umlsl_editor.src.core.dataclasses.road import LaneDirection


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


@dataclass
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
            CarValidationError: If any validation check fails.
        """
        # Validate direction type
        if not isinstance(self.direction, TurnDirection):
            raise TurnIntentValidationError(
                f"TurnIntent direction must be a TurnDirection enum value, "
                f"got {type(self.direction).__name__}: {self.direction}"
            )

        # Validate target_lane_index type
        if not isinstance(self.target_lane_index, int) or self.target_lane_index < 1:
            raise TurnIntentValidationError(
                f"TurnIntent target_lane_index must be a positive integer, "
                f"got {type(self.target_lane_index).__name__}: {self.target_lane_index}"
            )

        # Validate target_lane_direction type
        if not isinstance(self.target_lane_direction, LaneDirection):
            raise TurnIntentValidationError(
                f"TurnIntent target_lane_direction must be a LaneDirection enum value, "
                f"got {type(self.target_lane_direction).__name__}: {self.target_lane_direction}"
            )

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the TurnIntent instance to a dictionary suitable for JSON encoding.

        Returns:
            A dictionary containing:
                - 'direction': The turn direction as a string ('left' or 'right').
                - 'target_lane_index': The target lane index as an integer.
                - 'target_lane_direction': The target lane direction as a string ('fn' or 'bn').

        """
        return {
            "direction": self.direction.value,
            "target_lane_index": self.target_lane_index,
            "target_lane_direction": self.target_lane_direction.value,
        }

    def to_json(self) -> str:
        """
        Serializes the TurnIntent instance to a JSON string.

        Returns:
            A JSON-formatted string representation of the TurnIntent.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TurnIntent":
        """
        Creates a TurnIntent instance from a dictionary.

        Args:
            data: A dictionary containing 'direction', 'target_lane_index', and 'target_lane_direction' keys.
                  The 'direction' can be either a TurnDirection enum value
                  or a string ('left' or 'right').

        Returns:
            A new TurnIntent instance populated with the provided data.

        Raises:
            CarValidationError: If required keys are missing or values are invalid.

        """
        if "direction" not in data:
            raise TurnIntentValidationError(
                "Missing required key 'direction' in TurnIntent data"
            )
        if "target_lane_index" not in data:
            raise TurnIntentValidationError(
                "Missing required key 'target_lane_index' in TurnIntent data"
            )
        if "target_lane_direction" not in data:
            raise TurnIntentValidationError(
                "Missing required key 'target_lane_direction' in TurnIntent data"
            )

        # Parse direction - handle both string and enum values
        direction = data["direction"]
        if isinstance(direction, str):
            try:
                direction = TurnDirection(direction)
            except ValueError:
                raise TurnIntentValidationError(
                    f"Invalid direction value: '{direction}'. "
                    f"Must be one of: {[d.value for d in TurnDirection]}"
                )

        # Parse target_lane_index
        target_lane_index = data["target_lane_index"]
        if not isinstance(target_lane_index, int):
            raise TurnIntentValidationError(
                f"Invalid target_lane_index value: '{target_lane_index}'. "
                f"Must be an integer."
            )

        # Parse target_lane_direction - handle both string and enum values
        target_lane_direction = data["target_lane_direction"]
        if isinstance(target_lane_direction, str):
            try:
                target_lane_direction = LaneDirection(target_lane_direction)
            except ValueError:
                raise TurnIntentValidationError(
                    f"Invalid target_lane_direction value: '{target_lane_direction}'. "
                    f"Must be one of: {[d.value for d in LaneDirection]}"
                )

        return cls(
            direction=direction,
            target_lane_index=target_lane_index,
            target_lane_direction=target_lane_direction,
        )

    @classmethod
    def from_json(cls, json_string: str) -> "TurnIntent":
        """
        Creates a TurnIntent instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing turn intent data.

        Returns:
            A new TurnIntent instance populated with the parsed JSON data.

        Raises:
            CarValidationError: If the JSON structure is invalid or values fail validation.
            json.JSONDecodeError: If the string is not valid JSON.
        """
        data = json.loads(json_string)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the TurnIntent.

        Returns:
            A string in the format:
            TurnIntent(direction=DIRECTION, target_lane_index=INDEX, target_lane_direction=DIRECTION)
        """
        return (
            f"TurnIntent(direction={self.direction.name}, "
            f"target_lane_index={self.target_lane_index}, "
            f"target_lane_direction={self.target_lane_direction.name})"
        )
