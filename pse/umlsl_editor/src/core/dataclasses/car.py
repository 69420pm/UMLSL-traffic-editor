import json
import re
from dataclasses import dataclass
from typing import Any, ClassVar, Optional

from pse.umlsl_editor.src.core.dataclasses.entity import Entity
from pse.umlsl_editor.src.core.dataclasses.road import LaneDirection, Road, Lane
from pse.umlsl_editor.src.core.dataclasses.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.core.dataclasses.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.core.dataclasses.segments.segment import Path
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
        lane: Lane the car is currently in, defined by road, lane index, and direction.
        color: Hex color code for rendering.
        position_on_lane: Distance along the lane in units
        transition: Lane change progress from -1.0 to 1.0 exclusive
        velocity: Current speed of the car in units per time step
        length: Physical length of the car in units
        next_turn: Optional intended turn behavior at the next intersection
    """
    name: str
    lane: Lane
    color: str
    position_on_lane: float
    transition: float
    velocity: float
    length: float
    next_turn: Optional[TurnIntent]


@dataclass
class Car(Entity):
    """
    Represents a car/vehicle in the traffic simulation.

    A car is a movable entity that travels along lanes on roads. It has physical
    properties (length, color), kinematic properties (position, velocity), and
    navigational properties (assigned road, lane, transition state, next turn).

    Attributes:
        name: Unique human-readable identifier for the car. Must be a non-empty string.
        lane: Lane the car is currently in, defined by road, lane index, and direction.
        color: Hex color code for rendering the car.
        position_on_lane: Distance along the lane in units. Must be non-negative.
        transition: Lane change progress from -1.0 (fully left) to 1.0 (fully right).
                    Value of 0.0 means centered in current lane. Bounds are exclusive.
        velocity: Current speed of the car in units per time step. Can be negative for reverse.
        length: Physical length of the car in units. Must be positive.
        next_turn: Optional intended turn behavior at the next intersection.

        reserved_lanes: List of LaneSegments reserved by the car for future movement.
        claimed_lanes: List of LaneSegments currently claimed by the car.
        reserved_crossings: List of CrossingSegments reserved by the car.
        claimed_crossings: List of CrossingSegments currently claimed by the car.
        path: Path is list of LaneSegments and CrossingSegments representing the planned route.
        acceleration: Current acceleration of the car in units per time step squared.

    Raises:
        CarValidationError: If any validation check fails during instantiation.
    """


    lane: Lane

    color: str

    position_on_lane: float

    transition: float

    velocity: float

    length: float

    next_turn: Optional[TurnIntent]

    reserved_lanes: list[LaneSegment]

    claimed_lanes: list[LaneSegment]

    reserved_crossings: list[CrossingSegment]
    # todo: curr : I → Z such that curr(C ) is (the index - we save the object) of the path element of pth(C) currently occupied by the rear of C
    claimed_crossings: list[CrossingSegment]

    # todo: path pursued by car
    path: Path

    acceleration: float

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
            lane=params.lane,
            color=params.color,
            position_on_lane=params.position_on_lane,
            transition=params.transition,
            velocity=params.velocity,
            length=params.length,
            next_turn=params.next_turn,
            reserved_lanes=[],
            claimed_lanes=[],
            reserved_crossings=[],
            claimed_crossings=[],
            path=Path(segments=[]),
            acceleration=0.0,
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

    def absolute_position(self)-> float:
        return self.assigned_road.position + self.position_on_lane

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Car":
        """
        Creates a Car instance from a dictionary.

        Since the Car serialization only stores the road name (to avoid circular
        references), a road_lookup dictionary must be provided to resolve the
        actual Road object.

        Args:
            data: A dictionary containing car data with keys matching the to_dict output.

        """
        raise NotImplementedError()

    @classmethod
    def from_json(cls, json_string: str) -> "Car":
        """
        Creates a Car instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing car data.

        Returns:
            A new Car instance populated with the parsed JSON data.
        """

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Car.
        """
