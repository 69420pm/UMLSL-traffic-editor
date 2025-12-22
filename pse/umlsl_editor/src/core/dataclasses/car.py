from dataclasses import dataclass
from enum import Enum
from typing import Optional

from pse.umlsl_editor.src.core.dataclasses.lane import Lane
from pse.umlsl_editor.src.core.dataclasses.road import Road


class TurnDirection(Enum):
    LEFT = "left"
    RIGHT = "right"


@dataclass
class TurnIntent:
    """Encapsulates the 'Next Turn' logic tuple."""

    direction: TurnDirection
    """The direction of the intended turn (left or right)."""
    targetLane: Lane
    """The lane after the turn in which the car wants to turn"""


@dataclass
class Car:
    """
    Represents a car in the traffic simulation.
    """

    name: str
    """The unique human readable name of the car. Acts as an unique identifier."""

    assigned_road: Road
    """The direct reference to the road the car is currently on."""

    lane: Lane
    """The direct reference to lane the car is currently in. The lane must belong to the assigned road."""

    color: str = "#FF0000"
    """Hex color code for rendering the car."""

    position_on_lane: float = 0.0
    """Distance along the lane in units."""

    transition: float = 0.0
    """
    How far the car has changed from current lane (ranges from -1.0 to 1.0 (bounds excluded)).
    -1.0 means fully in left lane, 1.0 means fully in right lane.
    """

    velocity: float = 0.0
    """Current speed of the car."""

    length: float = 4.0
    """Physical length of the car in units."""

    next_turn: Optional[TurnIntent] = None
    """The intended turn direction and lane at the next intersection."""
