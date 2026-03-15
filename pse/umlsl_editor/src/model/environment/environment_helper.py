from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment


def compute_parallel_lane_segments(ts: TrafficSnapshotReader, segment: LaneSegment) -> list[LaneSegment]:
    """"
    Computes the segments parallel to the given lane segment.
    Parallel means that the segments are parallel to the driving direction of the lane segment.
    The given segment is included in the result, which is sorted by each segment's index.
    """

    assert segment.is_lane_segment
    lane_segment: LaneSegment = segment
    road = ts.get_road_by_uid(lane_segment.lane.road_uid)

    directions = [Direction.LEFT, Direction.RIGHT] if road.orientation == RoadOrientation.VERTICAL \
        else [Direction.UP, Direction.DOWN]

    segments: list[LaneSegment] = [segment]
    for direction in directions:
        next_segment = ts.get_adjacent_segment(segment.uid, direction)
        while next_segment is not None:
            # if we start on a lane segment and move orthogonal to its driving direction, we cannot reach a crossing
            # segment
            assert isinstance(next_segment, LaneSegment)
            segments.append(next_segment)
            next_segment = ts.get_adjacent_segment(next_segment.uid, direction)

    segments.sort(key=lambda seg: seg.lane.lane_index)
    return segments
