from dataclasses import dataclass, field

from pse.umlsl_editor.src.model.entities.road import Road, LaneDirection
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


@dataclass(frozen=True, kw_only=True)
class LaneSegment(Segment):
    lane: Lane
    length: float
    is_lane_segment: bool = field(default=True, init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.lane, Lane):
            raise ValueError("lane must be a Lane")
        if not isinstance(self.length, (int, float)) or self.length <= 0:
            raise ValueError("length must be a positive number")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LaneSegment):
            return NotImplemented
        return (self.lane == other.lane and
                self.length == other.length)

    def __hash__(self) -> int:
        return hash((self.lane, self.length))
