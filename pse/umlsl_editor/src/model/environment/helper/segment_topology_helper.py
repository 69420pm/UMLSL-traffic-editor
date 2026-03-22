from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.helper.direction import Direction
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


def compute_path(
        ts: TrafficSnapshotReader,
        start: LaneSegment,
        end: LaneSegment
) -> list[Segment] | None:
    """"
    Computes the path from start to end through a crossing segment using a column-like search algorithm.

    Args:
        ts: the traffic snapshot
        start: the starting segment
        end: the ending segment
    Returns:
        the list of segments through the crossing
    """
    if start.lane.road_uid == end.lane.road_uid:
        return _continue_path_straight(ts, start, end)

    path_through_crossing: list[Segment] = _compute_path_through_crossing(ts, start, end)
    if path_through_crossing is None:
        return None

    # after the turn, we continue straight in the direction of the last segment
    lane_segment_after_crossing: Segment = path_through_crossing[-1]
    if not isinstance(lane_segment_after_crossing, LaneSegment):
        raise ValueError(
            f"The last segment of the path through the crossing must be a lane segment."
        )
    remaining_path: list[Segment] = _continue_path_straight(ts, lane_segment_after_crossing, end)
    return path_through_crossing[:-1] + remaining_path


def _continue_path_straight(ts: TrafficSnapshotReader, start: LaneSegment, end: LaneSegment) -> list[Segment]:
    # we first have to figure out the direction of the path
    direction: Direction
    orientation_start: RoadOrientation = ts.get_road_by_uid(start.lane.road_uid).orientation
    orientation_end: RoadOrientation = ts.get_road_by_uid(end.lane.road_uid).orientation
    if orientation_start == RoadOrientation.HORIZONTAL and orientation_end == RoadOrientation.HORIZONTAL:
        direction = Direction.RIGHT if start.get_position(ts)[0] < end.get_position(ts)[0] else Direction.LEFT
    elif orientation_start == RoadOrientation.VERTICAL and orientation_end == RoadOrientation.VERTICAL:
        direction = Direction.UP if start.get_position(ts)[1] < end.get_position(ts)[1] else Direction.DOWN
    else:
        raise ValueError("Cannot compute straight path between segments of different orientations.")

    # we continue straight along that direction
    path: list[Segment] = [start]
    next_segment = ts.get_adjacent_segment(start.uid, direction)
    while next_segment is not None:
        path.append(next_segment)
        next_segment = ts.get_adjacent_segment(next_segment.uid, direction)

    return path


def _compute_path_through_crossing(ts: TrafficSnapshotReader, start: LaneSegment, end: LaneSegment) -> list[Segment] | None:
    relative_start_to_end = _compute_relative_direction(ts, start, end)
    relative_end_to_start = _compute_relative_direction(ts, end, start)

    # With this relative information, we can iterate in the opposite direction of "relative_start_to_end" (so we
    # iteratively enter the crossing). We call this segment the "search node". We then iterate from that search node
    # in the direction of "relative_end_to_start" to reach the final segment while always collecting the path data.
    search_node = ts.get_outgoing_adjacent_segment(start.uid, relative_start_to_end.opposite)
    forward_path: list[Segment] = [start, search_node]

    while search_node is not None:
        next_segment = ts.get_outgoing_adjacent_segment(search_node.uid, relative_end_to_start)

        path: list[Segment] = forward_path + [next_segment]
        while next_segment is not None:
            if next_segment == end:
                return path
            elif next_segment.is_lane_segment:
                break

            next_segment = ts.get_outgoing_adjacent_segment(next_segment.uid, relative_end_to_start)
            path.append(next_segment)

        search_node = ts.get_outgoing_adjacent_segment(search_node.uid, relative_start_to_end.opposite)
        forward_path.append(search_node)

    return None


def _compute_relative_direction(ts: TrafficSnapshotReader, lane1: LaneSegment, lane2: LaneSegment) -> Direction:
    pos1 = lane1.get_position(ts)
    pos2 = lane2.get_position(ts)

    orientation_1 = ts.get_road_by_uid(lane1.lane.road_uid).orientation
    if orientation_1 == RoadOrientation.VERTICAL:
        return Direction.DOWN if pos1[1] < pos2[1] else Direction.UP
    else:
        # horizontal
        return Direction.LEFT if pos1[0] < pos2[0] else Direction.RIGHT


def compute_parallel_lane_segments(ts: TrafficSnapshotReader, segment: LaneSegment, dist: int = -1) -> list[
    LaneSegment]:
    """"
    Computes the segments parallel to the given lane segment whose distance is <= the given distance away (set to -1
    to ignore).
    Parallel means that the segments are parallel to the driving direction of the lane segment.
    The given segment is included in the result, which is sorted by each segment's index.

    Args:
        ts: the traffic snapshot
        segment: the segment to compute the parallel segments for
        dist: how many lanes to expand in both directions, -1 to consider all parallel lane segments
    Returns:
        the list of parallel lane segments
    """

    assert segment.is_lane_segment
    lane_segment: LaneSegment = segment
    road = ts.get_road_by_uid(lane_segment.lane.road_uid)

    directions = [Direction.LEFT, Direction.RIGHT] if road.orientation == RoadOrientation.VERTICAL \
        else [Direction.UP, Direction.DOWN]

    segments: list[LaneSegment] = [segment]
    for direction in directions:
        next_segment = ts.get_adjacent_segment(segment.uid, direction)
        advancement = 0
        while next_segment is not None and (advancement < dist or dist == -1):
            # if we start on a lane segment and move orthogonal to its driving direction, we cannot reach a crossing
            # segment
            assert isinstance(next_segment, LaneSegment)
            segments.append(next_segment)
            next_segment = ts.get_adjacent_segment(next_segment.uid, direction)
            advancement += 1

    segments.sort(key=lambda seg: seg.lane.lane_index)
    return segments
