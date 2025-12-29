"""TypedDict definitions for entity creation parameters to enable type-safe **kwargs passing."""
from dataclasses import dataclass
from typing import Optional, TypedDict, Required, NotRequired

from pse.umlsl_editor.src.core.dataclasses.road import LaneDirection, Road, RoadOrientation
from pse.umlsl_editor.src.core.dataclasses.turn_intent import TurnIntent


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

@dataclass()
class RoadParams:
    """
    Type-safe parameter dictionary for Road creation.

    Supports all Road attributes with optional parameters marked appropriately.
    Use this with **kwargs to avoid repetitive parameter forwarding.

    Attributes:
        name: Unique human-readable identifier for the road.
        orientation: The orientation of the road (horizontal or vertical).
        position: The position of the road in the coordinate system.
        forward_lanes: Number of lanes in the forward direction
        backward_lanes: Number of lanes in the backward direction
    """
    name: str
    orientation: RoadOrientation
    position: float
    forward_lanes: int
    backward_lanes: int

