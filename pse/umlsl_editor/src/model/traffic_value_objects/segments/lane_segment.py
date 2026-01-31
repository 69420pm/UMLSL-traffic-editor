from dataclasses import dataclass, field

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import Direction
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
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

    def get_position(self, traffic_snapshot_reader: TrafficSnapshotReader) -> tuple[float, float]:
        """Return position of the top left corner of the lane segment.
        It gets calculated from the position of the lane and the road width."""
        left_adjacent_segment = traffic_snapshot_reader.get_adjacent_segment(self.uid, Direction.LEFT)
        top_adjacent_segment = traffic_snapshot_reader.get_adjacent_segment(self.uid, Direction.UP)

        if left_adjacent_segment is None:
            x = -float("inf")
        else:
            x = left_adjacent_segment.get_position(traffic_snapshot_reader)[0]
        if top_adjacent_segment is None:
            y = -float("inf")
        else:
            y = top_adjacent_segment.get_position(traffic_snapshot_reader)[1]
        return x, y

    def get_size(self, traffic_snapshot_reader: TrafficSnapshotReader) -> tuple[float, float]:
        """Return size (width, height) of the lane segment.
        It gets calculated from the road width and lane width."""
        left_adjacent_segment = traffic_snapshot_reader.get_adjacent_segment(self.uid, Direction.LEFT)
        right_adjacent_segment = traffic_snapshot_reader.get_adjacent_segment(self.uid, Direction.RIGHT)
        top_adjacent_segment = traffic_snapshot_reader.get_adjacent_segment(self.uid, Direction.UP)
        bottom_adjacent_segment = traffic_snapshot_reader.get_adjacent_segment(self.uid, Direction.DOWN)

        if left_adjacent_segment is None or right_adjacent_segment is None:
            width = float("inf")
        else:
            width = right_adjacent_segment.get_position(traffic_snapshot_reader)[0] - left_adjacent_segment.get_position(traffic_snapshot_reader)[0]
        if top_adjacent_segment is None or bottom_adjacent_segment is None:
            height = float("inf")
        else:
            height = bottom_adjacent_segment.get_position(traffic_snapshot_reader)[1] - top_adjacent_segment.get_position(traffic_snapshot_reader)[1]
        return width, height
