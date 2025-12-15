from typing import List, Optional

from pse.umlsl_editor.lane import Lane


class Road:
    """
    See Section 3.6.1.
    """
    def __init__(self, name: str, x: int, y: int, orientation: str):
        self.id: str = name  # Unique ID
        self.orientation = orientation
        self.position = (x, y)
        self.lanes: List[Lane] = []
        self.length: float = float('inf')  # Infinite

    def get_lane_by_id(self, lane_id: str) -> Optional[Lane]:
        pass