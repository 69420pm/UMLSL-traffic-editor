from pse.umlsl_editor.src.core.directions import LaneDirection


class Lane:
    """Represents a specific lane on a road."""

    def __init__(self, index: int, direction: LaneDirection):
        self.index = index
        self.direction = direction
