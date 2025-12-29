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
class CarParams:
    """
    Type-safe parameter dictionary for Car creation.

    Supports all Car attributes with optional parameters marked appropriately.
    Use this with **kwargs to avoid repetitive parameter forwarding.

    Attributes:
        name: Unique human-readable identifier for the car.
        assigned_road: Reference to the Road the car is currently traveling on.
        lane_index: Index of the lane the car is currently in.
        lane_direction: Direction of the lane the car is currently in.
        color: Hex color code for rendering.
        position_on_lane: Distance along the lane in units
        transition: Lane change progress from -1.0 to 1.0 exclusive
        velocity: Current speed of the car in units per time step
        length: Physical length of the car in units
        next_turn: Optional intended turn behavior at the next intersection
    """
    name: str
    assigned_road: Road
    lane_index: int
    lane_direction: LaneDirection
    color: str
    position_on_lane: float
    transition: float
    velocity: float
    length: float
    next_turn: Optional[TurnIntent]


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
        color: Hex color code for rendering the car.
        position_on_lane: Distance along the lane in units. Must be non-negative.
        transition: Lane change progress from -1.0 (fully left) to 1.0 (fully right).
                    Value of 0.0 means centered in current lane. Bounds are exclusive.
        velocity: Current speed of the car in units per time step. Can be negative for reverse.
        length: Physical length of the car in units. Must be positive.
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

    color: str

    position_on_lane: float

    transition: float

    velocity: float

    length: float

    next_turn: Optional[TurnIntent]

    @classmethod
    def from_params(cls, params: CarParams) -> "Car":
        """
        Creates a Car instance from a CarParams dataclass.

        Args:
            params: CarParams instance containing all car attributes.

        Returns:
            A new Car instance with attributes from the params.
        """
        return cls(
            name=params.name,
            assigned_road=params.assigned_road,
            lane_index=params.lane_index,
            lane_direction=params.lane_direction,
            color=params.color,
            position_on_lane=params.position_on_lane,
            transition=params.transition,
            velocity=params.velocity,
            length=params.length,
            next_turn=params.next_turn,
        )

    def __post_init__(self) -> None:
        """
        Validates the Car attributes after initialization without checking them in the TrafficSnapshot context.

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
    pass

    def update_from_params(self, params: CarParams) -> None:
        """
        Updates the Car instance's attributes based on a CarParams dataclass.

        Args:
            params: CarParams instance containing updated car attributes.

        Raises:
            CarValidationError: If any validation check fails.
        """
        raise NotImplementedError()


    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the Car instance to a dictionary suitable for JSON encoding.
        """
        raise NotImplementedError()


    def to_json(self) -> str:
        """
        Serializes the Car instance to a JSON string.

        Returns:
            A JSON-formatted string representation of the Car.
        """
        raise NotImplementedError()

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

        """
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json_string: str, road_lookup: dict[str, Road]) -> "Car":
        """
        Creates a Car instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing car data.
            road_lookup: A dictionary mapping road names to Road objects.

        Returns:
            A new Car instance populated with the parsed JSON data.
        """

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Car.
        """
