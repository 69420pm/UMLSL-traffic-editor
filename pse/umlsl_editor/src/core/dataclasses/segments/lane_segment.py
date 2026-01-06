from abc import ABC
from dataclasses import dataclass

from pse.umlsl_editor.src.core.dataclasses.road import Road, LaneDirection
from pse.umlsl_editor.src.core.dataclasses.segments.segment import Segment


@dataclass(frozen=True)
class LaneSegment(Segment):
    assigned_road: Road
    lane_index: int
    lane_direction: LaneDirection
    is_lane_segment: bool = True
