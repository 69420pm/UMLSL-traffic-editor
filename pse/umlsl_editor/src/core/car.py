from typing import Any, Optional

from pse.umlsl_editor.src.core.directions import TurnIntent


class Car:
    """
    Represents a car in the traffic simulation.
    """

    def __init__(
        self,
        name: str,
        assigned_road_id: str,
        lane_id: str,
        color: str = "#FF0000",
        position_on_lane: float = 0.0,
        velocity: float = 0.0,
        length: float = 4.0,
        next_turn: Optional[TurnIntent] = None,
    ):
        """
        Initialize a new Car instance.

        Args:
            id: The unique identifier for the car
            name: The human readable name of the car
            assigned_road_id: The ID of the road the car is currently on
            lane_id: The ID of the lane the car is currently in
            color: Hex color code for rendering the car (default: red "#FF0000")
            position_on_lane: Distance along the lane in units (default: 0.0)
            velocity: Current speed of the car (default: 0.0)
            length: Physical length of the car in units (default: 4.0)
            next_turn: The intended turn direction and lane at the next intersection (default: None)
        """
        self.id: str = ""
        self.name: str = name
        self.color: str = color
        self.assigned_road_id: str = assigned_road_id
        self.lane_id: str = lane_id
        self.position_on_lane: float = position_on_lane
        self.velocity: float = velocity
        self.length: float = length
        self.next_turn: Optional[TurnIntent] = next_turn
        self.safety_space_geometry: Any = None
