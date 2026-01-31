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
    is_lane_segment: bool = field(default=True, init=False)


    def __post_init__(self) -> None:
        if not isinstance(self.lane, Lane):
            raise ValueError("lane must be a Lane")

