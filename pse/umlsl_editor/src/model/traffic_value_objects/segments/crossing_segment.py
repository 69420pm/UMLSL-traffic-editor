from dataclasses import dataclass, field

from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.helper.uid_service import generate_uid
from pse.umlsl_editor.src.model.traffic_value_objects.position import Position
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


@dataclass(frozen=True, kw_only=True)
class CrossingSegment(Segment):
    horizontal_lane: Lane
    vertical_lane: Lane
    uid:str=field(default_factory=generate_uid)
    is_lane_segment: bool = field(default=False, init=False)


    def __post_init__(self) -> None:
        if not isinstance(self.horizontal_lane, Lane):
            raise ValueError("lane_horizontal must be a Lane")
        if not isinstance(self.vertical_lane, Lane):
            raise ValueError("lane_vertical must be a Lane")
        pass

    def get_position(self) -> Position:
        """Return position of the top left corner of the crossing segment.
        It gets calculated from the position of the two lanes."""
        raise NotImplementedError()
