from itertools import product

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.environment.environment_helper import compute_parallel_lane_segments
from pse.umlsl_editor.src.model.environment.segment_intervals_helper import compute_segment_intervals
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import VirtualLaneNew
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent, TurnDirection


def compute_path(
        ts: TrafficSnapshotReader,
        length: float,
        start_segment: LaneSegment,
        pos_on_segment: float,
        turn_intent: TurnIntent,
        car_direction: Direction,
        braking_dist: float
) -> tuple[list[Segment], list[SegmentInterval], list[SegmentInterval], LaneSegment, Interval]:
    """
    Returns the (path, turn_segment, horizontal horizon)

    For this, we first compute the unbounded path (that means stretching to the borders or (if a crossing occurs)
    stretching to the lane segment after the next crossing in the car's turn intent - no matter how far the crossing is
    away).
    We then compute the horizontal horizon (that means the maximum distance the car can come to a complete stand-still,
    and extend it until after the crossing if the car would otherwise stop on a crossing).
    We then iterate through our unbounded path and take only those segments that are within the horizontal horizon.
    Once we have the path, we also compute the segment intervals.
    """

    turn_segment: LaneSegment = _find_turn_intent_segment(ts, start_segment, turn_intent, car_direction)
    path: list[Segment] | None = _compute_path_through_crossing(ts, start_segment, turn_segment)
    if path is None:
        raise ValueError("Car specified a turn intent with invalid path.")

    horizontal_horizon = Interval(max(pos_on_segment - braking_dist, 0), pos_on_segment + braking_dist)

    physical_segment_intervals: list[SegmentInterval] = compute_segment_intervals(ts, path, pos_on_segment, length)
    path_segment_intervals: list[SegmentInterval] = compute_segment_intervals(
        ts,
        path,
        horizontal_horizon.start,
        horizontal_horizon.length(),
    )

    # If the turn intent exceeds what the car can see, we set the turn intent to the last lane segment.
    # For example, if the car turns left 1k units away but can only see 10 forward, the turn_segment gets useless.
    if turn_segment not in path:
        end_lane: Segment = path[-1]
        if not isinstance(end_lane, LaneSegment):
            raise ValueError("Path must end on a lane segment.")
        turn_segment = end_lane

    return path, physical_segment_intervals, path_segment_intervals, turn_segment, horizontal_horizon


def compute_parallel_virtual_lanes(
        ts: TrafficSnapshotReader,
        start_segment: LaneSegment,
        turn_direction: TurnDirection,
        turn_segment: LaneSegment,
        path: list[Segment],
        horizon: Interval
) -> list[list[VirtualLaneNew]]:
    parallel_segments = compute_parallel_segments(ts, start_segment, turn_segment, path, turn_direction)

    parallel_virtual_lanes: list[list[VirtualLaneNew]] = []
    for parallel_segment in parallel_segments:
        virtual_lanes: list[VirtualLaneNew] = []
        for segment_list in parallel_segment:
            virtual_lanes.append(segments_to_virtual_lane(horizon.start, segment_list, horizon, ts))
        parallel_virtual_lanes.append(virtual_lanes)

    return parallel_virtual_lanes


def segments_to_virtual_lane(pos_on_segment: float, segments: list[Segment], horizon: Interval,
                             ts: TrafficSnapshotReader) -> VirtualLaneNew:
    current_pos = pos_on_segment
    segment_intervals: list[SegmentInterval] = []

    for i, segment in enumerate(segments):
        # in the first iteration, we need to add the remaining length of the segment to the current position
        segment_size = segment.get_size_in_direction(ts)
        segment_length = (segment_size - current_pos) if i == 0 else segment_size

        physical_end = current_pos + segment_length
        view_end = min(physical_end, horizon.end)

        interval = Interval(current_pos, view_end)
        segment_intervals.append(SegmentInterval(segment, interval))

        if view_end < physical_end:
            break

        current_pos += segment_length

    return VirtualLaneNew(segment_intervals, [])


def compute_parallel_segments(
        ts: TrafficSnapshotReader,
        start_segment: LaneSegment,
        turn_segment: LaneSegment,
        path: list[Segment],
        turn_direction: TurnDirection
) -> list[list[list[Segment]]]:
    through_crossing = any(map(lambda seg: not seg.is_lane_segment, path))
    if through_crossing:
        return _compute_segments_through_crossing(
            ts,
            start_segment,
            turn_segment,
            turn_direction
        )
    else:
        # no crossing found
        parallel_lane_segments: list[LaneSegment] = compute_parallel_lane_segments(ts, start_segment)
        parallel_segments: list[list[Segment]] = []

        for parallel_lane_segment in parallel_lane_segments:
            parallel_segments.append([parallel_lane_segment])

        parallel_segments.sort(key=lambda lane: lane[0].lane.lane_index)

        return [parallel_segments]


def _compute_segments_through_crossing(
        ts: TrafficSnapshotReader,
        start_segment: LaneSegment,
        turn_segment: LaneSegment,
        turn_direction: TurnDirection
) -> list[list[list[Segment]]]:
    src_segments: list[LaneSegment] = compute_parallel_lane_segments(ts, start_segment, 1)
    start_road_orientation: RoadOrientation = ts.get_road_by_uid(start_segment.lane.road_uid).orientation

    if start_road_orientation == RoadOrientation.VERTICAL and turn_direction == TurnDirection.LEFT:
        src_segments.reverse()

    target_segments: list[LaneSegment] = compute_parallel_lane_segments(ts, turn_segment)

    def goes_into_crossing(segment: LaneSegment) -> bool:
        return _compute_path_through_crossing(ts, start_segment, segment) is not None

    order_lanes: list[list[list[Segment]]] = []
    for src_seg in src_segments:
        if goes_into_crossing(src_seg):
            if src_seg == start_segment:
                path: list[Segment] = _compute_path_through_crossing(ts, start_segment, turn_segment)
                if path is not None:
                    order_lanes.append([path])
            else:
                paths = []
                for target_segment in target_segments:
                    if not goes_into_crossing(target_segment):
                        continue
                    path: list[Segment] = _compute_path_through_crossing(ts, src_seg, target_segment)
                    if path is not None:
                        paths.append(path)
                order_lanes.append(paths)
        else:
            paths = []
            for target_segment in target_segments:
                if goes_into_crossing(target_segment):
                    continue
                path: list[Segment] = _compute_path_through_crossing(ts, target_segment, src_seg)
                if path is not None:
                    path.reverse()
                    paths.append(path)
            order_lanes.append(paths)

    parallel_lanes: list[list[list[Segment]]] = [list(p) for p in product(*order_lanes)]

    """
    DEBUG:
    for src_segment in src_segments:
        print("src segment: ", ts.get_segment_info(src_segment.uid), " into=", goes_into_crossing(src_segment))
    for target_segment in target_segments:
        print("target segment: ", ts.get_segment_info(target_segment.uid), " into=", goes_into_crossing(target_segment))
        
    print("ordered lanes:")
    for order_lane in order_lanes:
        print("next ord lane", list(map(lambda x: list(map(lambda y: ts.get_segment_info(y.uid), x)), order_lane)))
    for parallel_lane in parallel_lanes:
        print("parallel lane: ")
        for e in parallel_lane:
            print(list(map(lambda x: ts.get_segment_info(x.uid), e)))
    """

    return parallel_lanes


def _find_turn_intent_segment(
        ts: TrafficSnapshotReader,
        start: LaneSegment,
        turn_intent: TurnIntent,
        car_direction: Direction
) -> LaneSegment:
    """"
    We need to find the target lane segment based on the turn intent and the car's current position.
    Since we know the target lane, we can collect all lane(!) segments of the target lane first.
    Each segment has a two-dimensional position, but to find the target segment, it is enough to compare only 1 coordinate:
    For example, if the car is driving straight, we only need to compare the x coordinate to find the segment and find
    the first segment with a larger x coordinate than the starting segment.
    """
    start_coords = start.get_position(ts)
    # we need to find the target lane segment based on the turn intent

    # collect all segments of the target lane
    segments_of_target_lane: list[Segment] = []
    for segment in ts.all_segments():
        if isinstance(segment, LaneSegment):
            lane_segment: LaneSegment = segment
            if lane_segment.lane == turn_intent.target_lane:
                segments_of_target_lane.append(segment)

    turn_direction = turn_intent.direction
    start_road_direction = ts.get_road_by_uid(start.lane.road_uid).orientation

    # if there is no crossing on the road (-> 1 lane segment), we can terminate directly
    if len(segments_of_target_lane) == 1:
        assert turn_direction == TurnDirection.STRAIGHT
        return segments_of_target_lane[0]

    # for straight driving, we can iterate straight through the crossing and take the first lane segment
    if turn_direction == TurnDirection.STRAIGHT:
        next_segment = ts.get_adjacent_segment(start.uid, car_direction)
        if next_segment is None and start.is_lane_segment:
            return start
        while next_segment is not None:
            if isinstance(next_segment, LaneSegment):
                return next_segment
            next_segment = ts.get_adjacent_segment(next_segment.uid, car_direction)

    # the segment_position_index is used to consider only the relevant coordinate of the segments_of_target_lane list
    segment_position_index: int = 1 if start_road_direction == RoadOrientation.HORIZONTAL else 0
    segments_of_target_lane.sort(key=lambda x: x.get_position(ts)[segment_position_index])

    if car_direction in {Direction.LEFT, Direction.UP}:
        if turn_direction == TurnDirection.LEFT:
            segments_of_target_lane.reverse()

            for segment in segments_of_target_lane:
                pos = segment.get_position(ts)[segment_position_index]
                start_pos = start_coords[segment_position_index]
                if isinstance(segment, LaneSegment) and pos < start_pos:
                    return segment
        else:
            for segment in segments_of_target_lane:
                pos = segment.get_position(ts)[segment_position_index]
                start_pos = start_coords[segment_position_index]
                if isinstance(segment, LaneSegment) and pos > start_pos:
                    return segment
    else:
        if turn_direction == TurnDirection.RIGHT:
            segments_of_target_lane.reverse()

            for segment in segments_of_target_lane:
                pos = segment.get_position(ts)[segment_position_index]
                start_pos = start_coords[segment_position_index]
                if isinstance(segment, LaneSegment) and pos < start_pos:
                    return segment
        else:
            for segment in segments_of_target_lane:
                pos = segment.get_position(ts)[segment_position_index]
                start_pos = start_coords[segment_position_index]
                if isinstance(segment, LaneSegment) and pos > start_pos:
                    return segment

    raise ValueError("Turn intent not found.")


def _compute_path_through_crossing(
        ts: TrafficSnapshotReader,
        start: LaneSegment,
        end: LaneSegment
) -> list[Segment] | None:
    """"
    Computes the path from start to end through a crossing segment.
    """
    if start == end:
        return [start]

    relative_start_to_end = _compute_relative_direction(ts, start, end)
    relative_end_to_start = _compute_relative_direction(ts, end, start)

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
