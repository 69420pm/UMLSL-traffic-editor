from dataclasses import dataclass

from pse.umlsl_editor.src.model.entities.road import Road, LaneDirection
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


@dataclass(frozen=True, kw_only=True)
class LaneSegment(Segment):
    assigned_road: Road
    lane_index: int
    lane_direction: LaneDirection
    is_lane_segment: bool = True

    def __post_init__(self) -> None:
        if not isinstance(self.assigned_road, Road):
            raise ValueError("assigned_road must be a Road")
        if not isinstance(self.lane_index, int) or self.lane_index < 1:
            raise ValueError("lane_index must be a positive integer")
        if not isinstance(self.lane_direction, LaneDirection):
            raise ValueError("lane_direction must be a LaneDirection")
        if not isinstance(self.length, (int, float)) or self.length <= 0:
            raise ValueError("length must be a positive number")
