from dataclasses import dataclass
from enum import Enum
from typing import Any


class LaneDirection(Enum):
    """
    Enumeration representing the direction of traffic flow in a lane.

    Attributes:
        FORWARD: Traffic flows in the forward direction (represented as 'fn').
        BACKWARD: Traffic flows in the backward direction (represented as 'bn').
    """

    FORWARD = "fn"
    BACKWARD = "bn"


class LaneValidationError(ValueError):
    """
    Custom exception raised when Lane validation fails.
    """

    pass


@dataclass
class Lane:
    """
    Represents a specific lane on a road in a traffic snapshot.

    Attributes:
        index: The 1-based index of the lane on the road, counted from the inside out.
               Must be a positive integer (>= 1).
        direction: The direction of traffic flow in this lane.
                   Can be FORWARD ('fn') or BACKWARD ('bn').

    Raises:
        LaneValidationError: If index is not a positive integer or direction is invalid.
    """

    index: int

    direction: LaneDirection

    def __post_init__(self) -> None:
        """
        Validates the Lane instance after initialization.

        Performs the following validation checks:
        - index must be an integer
        - index must be positive (>= 1)
        - direction must be a valid LaneDirection enum value

        Raises:
            LaneValidationError: If any validation check fails.
        """
        # Validate index type
        if not isinstance(self.index, int):
            raise LaneValidationError(
                f"Lane index must be an integer, got {type(self.index).__name__}: {self.index}"
            )

        # Validate index value (must be positive, 1-based indexing)
        if self.index < 1:
            raise LaneValidationError(
                f"Lane index must be a positive integer (>= 1), got: {self.index}"
            )

        # Validate direction type
        if not isinstance(self.direction, LaneDirection):
            raise LaneValidationError(
                f"Lane direction must be a LaneDirection enum value, "
                f"got {type(self.direction).__name__}: {self.direction}"
            )

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the Lane instance to a dictionary suitable for JSON encoding.

        Returns:
            A dictionary containing:
                - 'index': The lane index as an integer.
                - 'direction': The direction value as a string ('fn' or 'bn').
        """
        return {"index": self.index, "direction": self.direction.value}

    def to_json(self) -> str:
        """
        Serializes the Lane instance to a JSON string.

        Returns:
            A JSON-formatted string representation of the Lane.
        """
        import json

        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Lane":
        """
        Creates a Lane instance from a dictionary.

        Args:
            data: A dictionary containing 'index' and 'direction' keys.
                  The 'direction' can be either a LaneDirection enum value
                  or a string ('fn' or 'bn').

        Returns:
            A new Lane instance populated with the provided data.

        Raises:
            LaneValidationError: If required keys are missing or values are invalid.
            KeyError: If required keys are missing from the dictionary.

        Example:
            >>> data = {'index': 1, 'direction': 'fn'}
            >>> lane = Lane.from_dict(data)
            >>> lane.index
            1
        """
        if "index" not in data:
            raise LaneValidationError("Missing required key 'index' in Lane data")
        if "direction" not in data:
            raise LaneValidationError("Missing required key 'direction' in Lane data")

        # Parse direction - handle both string and enum values
        direction = data["direction"]
        if isinstance(direction, str):
            try:
                direction = LaneDirection(direction)
            except ValueError:
                raise LaneValidationError(
                    f"Invalid direction value: '{direction}'. "
                    f"Must be one of: {[d.value for d in LaneDirection]}"
                )

        return cls(index=data["index"], direction=direction)

    @classmethod
    def from_json(cls, json_string: str) -> "Lane":
        """
        Creates a Lane instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing lane data.

        Returns:
            A new Lane instance populated with the parsed JSON data.

        Raises:
            LaneValidationError: If the JSON structure is invalid or values fail validation.
            json.JSONDecodeError: If the string is not valid JSON.

        Example:
            >>> json_str = '{"index": 1, "direction": "fn"}'
            >>> lane = Lane.from_json(json_str)
            >>> lane.direction
            <LaneDirection.FORWARD: 'fn'>
        """
        import json

        data = json.loads(json_string)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Lane.

        Returns:
            A string in the format: Lane(index=X, direction=DIRECTION)
        """
        return f"Lane(index={self.index}, direction={self.direction.name})"
