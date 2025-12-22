import json
import re
from dataclasses import dataclass
from typing import Any, ClassVar, Optional

from pse.umlsl_editor.src.core.dataclasses.road import LaneDirection, Road
from pse.umlsl_editor.src.core.dataclasses.turn_intent import TurnDirection, TurnIntent


class CarValidationError(ValueError):
    """
    Custom exception raised when a Car validation fails.
    """

    pass


@dataclass
class Car:
    """
    Represents a car/vehicle in the traffic simulation.

    A car is a movable entity that travels along lanes on roads. It has physical
    properties (length, color), kinematic properties (position, velocity), and
    navigational properties (assigned road, lane, transition state, next turn).

    Attributes:
        name: Unique human-readable identifier for the car. Must be a non-empty string.
        assigned_road: Reference to the Road the car is currently traveling on.
        lane_index: Index of the lane the car is currently in.
        lane_direction: Direction of the lane the car is currently in.
        color: Hex color code for rendering the car. Defaults to red (#FF0000).
        position_on_lane: Distance along the lane in units. Must be non-negative. Defaults to 0.0.
        transition: Lane change progress from -1.0 (fully left) to 1.0 (fully right).
                    Value of 0.0 means centered in current lane. Bounds are exclusive.
        velocity: Current speed of the car in units per time step. Can be negative for reverse.
        length: Physical length of the car in units. Must be positive. Defaults to 4.0.
        next_turn: Optional intended turn behavior at the next intersection.

    Raises:
        CarValidationError: If any validation check fails during instantiation.
    """

    # Class-level regex pattern for validating hex color codes
    _HEX_COLOR_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$"
    )

    name: str

    assigned_road: Road

    lane_index: int
    lane_direction: LaneDirection

    color: str = "#FF0000"

    position_on_lane: float = 0.0

    transition: float = 0.0

    velocity: float = 0.0

    length: float = 4.0

    next_turn: Optional[TurnIntent] = None

    def __post_init__(self) -> None:
        """
        Validates the Car instance after initialization.

        Performs the following validation checks:
        - name must be a non-empty string
        - assigned_road must be a Road instance
        - lane_index must be a positive integer
        - lane_direction must be a LaneDirection enum value
        - color must be a valid hex color code
        - position_on_lane must be a non-negative number
        - transition must be in the range (-1.0, 1.0) exclusive
        - velocity must be a number
        - length must be a positive number
        - next_turn must be None or a TurnIntent instance

        Raises:
            CarValidationError: If any validation check fails.
        """
        # Validate name
        if not isinstance(self.name, str):
            raise CarValidationError(
                f"Car name must be a string, got {type(self.name).__name__}: {self.name}"
            )
        if not self.name.strip():
            raise CarValidationError("Car name cannot be empty or whitespace only")

        # Validate assigned_road
        if not isinstance(self.assigned_road, Road):
            raise CarValidationError(
                f"Car assigned_road must be a Road instance, "
                f"got {type(self.assigned_road).__name__}"
            )

        # Validate lane_index
        if not isinstance(self.lane_index, int) or self.lane_index < 1:
            raise CarValidationError(
                f"Car lane_index must be a positive integer, "
                f"got {type(self.lane_index).__name__}: {self.lane_index}"
            )

        # Validate lane_direction
        if not isinstance(self.lane_direction, LaneDirection):
            raise CarValidationError(
                f"Car lane_direction must be a LaneDirection enum value, "
                f"got {type(self.lane_direction).__name__}: {self.lane_direction}"
            )

        # Validate color format (hex color code)
        if not isinstance(self.color, str):
            raise CarValidationError(
                f"Car color must be a string, got {type(self.color).__name__}"
            )
        if not self._is_valid_hex_color(self.color):
            raise CarValidationError(
                f"Car color must be a valid hex color code (e.g., '#FF0000' or '#F00'), "
                f"got: '{self.color}'"
            )

        # Validate position_on_lane
        if not isinstance(self.position_on_lane, (int, float)):
            raise CarValidationError(
                f"Car position_on_lane must be a number, "
                f"got {type(self.position_on_lane).__name__}"
            )
        if self.position_on_lane < 0:
            raise CarValidationError(
                f"Car position_on_lane must be non-negative, got: {self.position_on_lane}"
            )

        # Validate transition
        if not isinstance(self.transition, (int, float)):
            raise CarValidationError(
                f"Car transition must be a number, got {type(self.transition).__name__}"
            )
        if not (-1.0 < self.transition < 1.0):
            raise CarValidationError(
                f"Car transition must be in range (-1.0, 1.0) exclusive, got: {self.transition}"
            )

        # Validate velocity
        if not isinstance(self.velocity, (int, float)):
            raise CarValidationError(
                f"Car velocity must be a number, got {type(self.velocity).__name__}"
            )

        # Validate length
        if not isinstance(self.length, (int, float)):
            raise CarValidationError(
                f"Car length must be a number, got {type(self.length).__name__}"
            )
        if self.length <= 0:
            raise CarValidationError(
                f"Car length must be a positive number, got: {self.length}"
            )

        # Validate next_turn
        if self.next_turn is not None and not isinstance(self.next_turn, TurnIntent):
            raise CarValidationError(
                f"Car next_turn must be None or a TurnIntent instance, "
                f"got {type(self.next_turn).__name__}"
            )

    @classmethod
    def _is_valid_hex_color(cls, color: str) -> bool:
        """
        Validates whether a string is a valid hex color code.

        Accepts both 3-character shorthand (#RGB) and 6-character full (#RRGGBB)
        hex color codes, case-insensitive.

        Args:
            color: The string to validate as a hex color code.

        Returns:
            True if the string is a valid hex color code, False otherwise.
        """
        return bool(cls._HEX_COLOR_PATTERN.match(color))

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the Car instance to a dictionary suitable for JSON encoding.

        The assigned_road is serialized by name only to avoid circular references.
        Use the road name to look up the full Road object when deserializing.

        Returns:
            A dictionary containing all car properties:
                - 'name': The car name as a string.
                - 'assigned_road': The road name as a string.
                - 'lane_index': The lane index as an integer.
                - 'lane_direction': The lane direction as a string ('fn' or 'bn').
                - 'color': The hex color code as a string.
                - 'position_on_lane': The position as a float.
                - 'transition': The transition value as a float.
                - 'velocity': The velocity as a float.
                - 'length': The length as a float.
                - 'next_turn': The turn intent as a dictionary, or None.
        """
        return {
            "name": self.name,
            "assigned_road": self.assigned_road.name,
            "lane_index": self.lane_index,
            "lane_direction": self.lane_direction.value,
            "color": self.color,
            "position_on_lane": self.position_on_lane,
            "transition": self.transition,
            "velocity": self.velocity,
            "length": self.length,
            "next_turn": self.next_turn.to_dict() if self.next_turn else None,
        }

    def to_json(self) -> str:
        """
        Serializes the Car instance to a JSON string.

        Returns:
            A JSON-formatted string representation of the Car.
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any], road_lookup: dict[str, Road]) -> "Car":
        """
        Creates a Car instance from a dictionary.

        Since the Car serialization only stores the road name (to avoid circular
        references), a road_lookup dictionary must be provided to resolve the
        actual Road object.

        Args:
            data: A dictionary containing car data with keys matching the to_dict output.
            road_lookup: A dictionary mapping road names to Road objects.

        Returns:
            A new Car instance populated with the provided data.

        Raises:
            CarValidationError: If required keys are missing, road is not found,
                                or values fail validation.

        """
        required_keys = ["name", "assigned_road", "lane_index", "lane_direction"]
        for key in required_keys:
            if key not in data:
                raise CarValidationError(f"Missing required key '{key}' in Car data")

        # Resolve assigned_road from lookup
        road_name = data["assigned_road"]
        if road_name not in road_lookup:
            raise CarValidationError(
                f"Road '{road_name}' not found in road_lookup. "
                f"Available roads: {list(road_lookup.keys())}"
            )
        assigned_road = road_lookup[road_name]

        # Parse lane_index
        lane_index = data["lane_index"]
        if not isinstance(lane_index, int):
            raise CarValidationError(
                f"Invalid lane_index value: '{lane_index}'. Must be an integer."
            )

        # Parse lane_direction - handle both string and enum values
        lane_direction = data["lane_direction"]
        if isinstance(lane_direction, str):
            try:
                lane_direction = LaneDirection(lane_direction)
            except ValueError:
                raise CarValidationError(
                    f"Invalid lane_direction value: '{lane_direction}'. "
                    f"Must be one of: {[d.value for d in LaneDirection]}"
                )

        # Parse next_turn if present
        next_turn = None
        if data.get("next_turn") is not None:
            next_turn_data = data["next_turn"]
            if isinstance(next_turn_data, dict):
                next_turn = TurnIntent.from_dict(next_turn_data)
            elif isinstance(next_turn_data, TurnIntent):
                next_turn = next_turn_data
            else:
                raise CarValidationError(
                    f"Invalid next_turn data type: {type(next_turn_data).__name__}"
                )

        return cls(
            name=data["name"],
            assigned_road=assigned_road,
            lane_index=lane_index,
            lane_direction=lane_direction,
            color=data.get("color", "#FF0000"),
            position_on_lane=data.get("position_on_lane", 0.0),
            transition=data.get("transition", 0.0),
            velocity=data.get("velocity", 0.0),
            length=data.get("length", 4.0),
            next_turn=next_turn,
        )

    @classmethod
    def from_json(cls, json_string: str, road_lookup: dict[str, Road]) -> "Car":
        """
        Creates a Car instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing car data.
            road_lookup: A dictionary mapping road names to Road objects.

        Returns:
            A new Car instance populated with the parsed JSON data.

        Raises:
            CarValidationError: If the JSON structure is invalid or values fail validation.
            json.JSONDecodeError: If the string is not valid JSON.
        """
        data = json.loads(json_string)
        return cls.from_dict(data, road_lookup)

    def set_next_turn(
        self,
        direction: TurnDirection,
        target_lane_index: int,
        target_lane_direction: LaneDirection,
    ) -> None:
        """
        Sets the car's next turn intent, by creating a new TurnIntent instance,
        where all values are validated.

        Args:
            direction: The direction of the intended turn (LEFT or RIGHT).
            target_lane_index: The index of the target lane the car wants to enter after the turn.
            target_lane_direction: The direction of the target lane (FORWARD or BACKWARD).

        Raises:
            CarValidationError: If the TurnIntent validation fails.
        """
        self.next_turn = TurnIntent(
            direction=direction,
            target_lane_index=target_lane_index,
            target_lane_direction=target_lane_direction,
        )

    def clear_next_turn(self) -> None:
        """
        Clears the car's next turn intent, indicating the car has no planned turn.
        """
        self.next_turn = None

    def is_in_lane_transition(self) -> bool:
        """
        Checks if the car is currently changing lanes.

        A car is considered to be in lane transition if its transition
        value is not zero (i.e., not centered in its current lane).

        Returns:
            True if the car is in the process of changing lanes, False otherwise.
        """
        return abs(self.transition) > 1e-9

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Car.

        Returns:
            A string showing the car's key properties including name, road,
            lane, position, velocity, and turn intent status.
        """
        turn_info = (
            f", next_turn={self.next_turn.direction.name}" if self.next_turn else ""
        )
        return (
            f"Car(name='{self.name}', road='{self.assigned_road.name}', "
            f"lane_index={self.lane_index}, lane_direction={self.lane_direction.name}, "
            f"pos={self.position_on_lane:.1f}, vel={self.velocity:.1f}{turn_info})"
        )
