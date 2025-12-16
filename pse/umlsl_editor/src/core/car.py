from dataclasses import dataclass, field
from typing import Optional

from pse.umlsl_editor.src.core.directions import TurnIntent


@dataclass
class Car:
    """
    Represents a car in the traffic simulation.
    """

    name: str
    """The human readable name of the car."""

    assigned_road_id: str
    """The ID of the road the car is currently on."""

    lane_id: str
    """The ID of the lane the car is currently in."""

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

    # Fields below are not required in the constructor (init=False)

    id: str = field(default="", init=False)
    """The unique identifier for the car."""
