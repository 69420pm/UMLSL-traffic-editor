from dataclasses import dataclass

from pse.umlsl_editor.src.model.value_objects.lane import Lane
from pse.umlsl_editor.src.model.value_objects.position import Position
from pse.umlsl_editor.src.model.value_objects.segments.segment import Segment


@dataclass(frozen=True)
class CrossingSegment(Segment):
    lane_horizontal: Lane
    lane_vertical: Lane
    is_lane_segment = True

    def get_position(self) -> Position:
        """Return position of the top left corner of the crossing segment.
        It gets calculated from the position of the two lanes."""
        raise NotImplementedError()


