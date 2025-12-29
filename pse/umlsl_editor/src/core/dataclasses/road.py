from dataclasses import dataclass
from enum import Enum
from typing import Any

from pse.umlsl_editor.src.core.dataclasses.params import RoadParams


class RoadOrientation(Enum):
    """
    Enumeration representing the orientation of a road in the coordinate system.

    Attributes:
        HORIZONTAL: The road runs horizontally (left-right) in the coordinate system.
        VERTICAL: The road runs vertically (up-down) in the coordinate system.
    """

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class LaneDirection(Enum):
    """
    Enumeration representing the direction of traffic flow in a lane.

    Attributes:
        FORWARD: Traffic flows in the forward direction (represented as 'fn').
        BACKWARD: Traffic flows in the backward direction (represented as 'bn').
    """

    FORWARD = "fn"
    BACKWARD = "bn"


class RoadValidationError(ValueError):
    """
    Custom exception raised when Road validation fails.
    """

    pass


@dataclass
class Road:
    """
    Represents a road in the traffic simulation system.

    A road is an infinite linear line with a specific orientation (horizontal or vertical)
    and contains one or more lanes in either forward or backward direction.
    Roads only define the number of forward and backward lanes.

    Attributes:
        name: Unique human-readable identifier for the road.
              Must be a non-empty string.
        orientation: The orientation of the road (HORIZONTAL or VERTICAL).
        position: The position of the road in the coordinate system along the
                  axis perpendicular to its orientation. For horizontal roads,
                  this is the Y-coordinate; for vertical roads, the X-coordinate.
        forward_lanes: Number of lanes in the forward direction
        backward_lanes: Number of lanes in the backward direction

    Raises:
        RoadValidationError: If name is empty, orientation is invalid,
                             or position is not a valid number.
    """

    name: str
    orientation: RoadOrientation
    position: float
    forward_lanes: int
    backward_lanes: int

    @classmethod
    def from_params(cls, params: RoadParams) -> "Road":
        """
        Creates a Road instance from a RoadParams object.

        Args:
            params: An instance of RoadParams containing the road attributes.
        Returns:
            A new Road instance with the provided parameters.
        """
        return cls(
            name=params.name,
            orientation=params.orientation,
            position=params.position,
            forward_lanes=params.forward_lanes,
            backward_lanes=params.backward_lanes,
        )


    def __post_init__(self) -> None:
        """
        Validates the Road instance after initialization.

        Performs the following validation checks:
        - name must be a non-empty string
        - orientation must be a valid RoadOrientation enum value
        - position must be a valid number (int or float)
        - forward_lanes and backward_lanes must be non-negative integers

        Raises:
            RoadValidationError: If any validation check fails.
        """
        # Validate name type and value
        if not isinstance(self.name, str):
            raise RoadValidationError(
                f"Road name must be a string, got {type(self.name).__name__}: {self.name}"
            )
        if not self.name.strip():
            raise RoadValidationError("Road name cannot be empty or whitespace only")

        # Validate orientation type
        if not isinstance(self.orientation, RoadOrientation):
            raise RoadValidationError(
                f"Road orientation must be a RoadOrientation enum value, "
                f"got {type(self.orientation).__name__}: {self.orientation}"
            )

        # Validate position type
        if not isinstance(self.position, (int, float)):
            raise RoadValidationError(
                f"Road position must be a number (int or float), "
                f"got {type(self.position).__name__}: {self.position}"
            )

        # Validate forward_lanes and backward_lanes type and value
        if not isinstance(self.forward_lanes, int) or self.forward_lanes < 0:
            raise RoadValidationError(
                f"forward_lanes must be a non-negative integer, got {self.forward_lanes}"
            )
        if not isinstance(self.backward_lanes, int) or self.backward_lanes < 0:
            raise RoadValidationError(
                f"backward_lanes must be a non-negative integer, got {self.backward_lanes}"
            )

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the Road instance to a dictionary suitable for JSON encoding.

        Returns:
            A dictionary containing:
                - 'name': The road name as a string.
                - 'orientation': The orientation value as a string ('horizontal' or 'vertical').
                - 'position': The position as a float.
                - 'forward_lanes': The number of forward lanes as an integer.
                - 'backward_lanes': The number of backward lanes as an integer.

        Example:
            >>> road = Road(name="Main St", orientation=RoadOrientation.HORIZONTAL, position=100.0, forward_lanes=2, backward_lanes=1)
            >>> road.to_dict()
            {'name': 'Main St', 'orientation': 'horizontal', 'position': 100.0, 'forward_lanes': 2, 'backward_lanes': 1}
        """
        return {
            "name": self.name,
            "orientation": self.orientation.value,
            "position": self.position,
            "forward_lanes": self.forward_lanes,
            "backward_lanes": self.backward_lanes,
        }

    def to_json(self) -> str:
        """
        Serializes the Road instance to a JSON string.

        Returns:
            A JSON-formatted string representation of the Road.

        Example:
            >>> road = Road(name="Main St", orientation=RoadOrientation.HORIZONTAL, position=100.0, forward_lanes=2, backward_lanes=1)
            >>> road.to_json()
            '{"name": "Main St", "orientation": "horizontal", "position": 100.0, "forward_lanes": 2, "backward_lanes": 1}'
        """
        import json

        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Road":
        """
        Creates a Road instance from a dictionary.

        Args:
            data: A dictionary containing 'name', 'orientation', 'position',
                  and optionally 'forward_lanes' and 'backward_lanes' keys.
                  The 'orientation' can be either a RoadOrientation enum value
                  or a string ('horizontal' or 'vertical').

        Returns:
            A new Road instance populated with the provided data.

        Raises:
            RoadValidationError: If required keys are missing or values are invalid.

        Example:
            >>> data = {'name': 'Main St', 'orientation': 'horizontal', 'position': 100.0, 'forward_lanes': 2, 'backward_lanes': 1}
            >>> road = Road.from_dict(data)
            >>> road.name
            'Main St'
        """
        required_keys = ["name", "orientation", "position"]
        for key in required_keys:
            if key not in data:
                raise RoadValidationError(f"Missing required key '{key}' in Road data")

        # Parse orientation - handle both string and enum values
        orientation = data["orientation"]
        if isinstance(orientation, str):
            try:
                orientation = RoadOrientation(orientation)
            except ValueError:
                raise RoadValidationError(
                    f"Invalid orientation value: '{orientation}'. "
                    f"Must be one of: {[o.value for o in RoadOrientation]}"
                )

        return cls(
            name=data["name"],
            orientation=orientation,
            position=data["position"],
            forward_lanes=data.get("forward_lanes", 0),
            backward_lanes=data.get("backward_lanes", 0),
        )

    @classmethod
    def from_json(cls, json_string: str) -> "Road":
        """
        Creates a Road instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing road data.

        Returns:
            A new Road instance populated with the parsed JSON data.

        Raises:
            RoadValidationError: If the JSON structure is invalid or values fail validation.
            json.JSONDecodeError: If the string is not valid JSON.

        Example:
            >>> json_str = '{"name": "Main St", "orientation": "horizontal", "position": 100.0, "forward_lanes": 2, "backward_lanes": 1}'
            >>> road = Road.from_json(json_str)
            >>> road.orientation
            <RoadOrientation.HORIZONTAL: 'horizontal'>
        """
        import json

        data = json.loads(json_string)
        return cls.from_dict(data)

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Road.

        Returns:
            A string in the format: Road(name='X', orientation=ORIENTATION, position=Y, forward_lanes=F, backward_lanes=B)
        """
        return (
            f"Road(name='{self.name}', orientation={self.orientation.name}, "
            f"position={self.position}, forward_lanes={self.forward_lanes}, backward_lanes={self.backward_lanes})"
        )
