from typing import Optional, Any

from pse.umlsl_editor.directions import TurnIntent


class Car:
    """
    See Section 3.6.2.
    """
    def __init__(self, name: str):
        self.id: str = name
        self.color: str = "#FF0000"
        self.assigned_road_id: str = ""
        self.lane_id: str = "f1"
        self.position_on_lane: float = 0.0
        self.velocity: float = 0.0
        self.length: float = 4.0
        self.next_turn: Optional[TurnIntent] = None
        self.safety_space_geometry: Any = None  # Cached geometry