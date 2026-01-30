from dataclasses import dataclass, field

from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.helper.uid_service import generate_uid
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


@dataclass(frozen=True, kw_only=True)
class LaneSegment(Segment):
    """The lane segment describes a segment of a single lane between two perpendicular roads."""
    uid: str = field(default_factory=generate_uid)
    lane: Lane
    """The lane on which the segment is located"""
    start_crossing: str|None
    """The start crossing uid which marks the start of the segment"""
    end_crossing: str|None
    """The end crossing uid which marks the end of the segment"""
    is_lane_segment: bool = field(default=True, init=False)


    def __post_init__(self) -> None:
        if not isinstance(self.lane, Lane):
            raise ValueError("lane must be a Lane")
        if not isinstance(self.start_crossing, str):
            raise ValueError("start_road must be a string")
        if not isinstance(self.end_crossing, str):
            raise ValueError("end_road must be a string")
