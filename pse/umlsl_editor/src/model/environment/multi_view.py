from collections import deque

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.environment.environment_helper import compute_parallel_lane_segments
from pse.umlsl_editor.src.model.environment.segment_intervals_helper import compute_segment_intervals, \
    compute_segments_safety_envelope
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import VirtualLane, VirtualLaneNew
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent, TurnDirection


def compute_path(
        ts: TrafficSnapshotReader,
        length: float,
        start_segment: LaneSegment,
        pos_on_segment: float,
        turn_intent: TurnIntent,
        car_direction: Direction,
        braking_dist: float
) -> tuple[VirtualLane, list[SegmentInterval], list[SegmentInterval], LaneSegment, Interval]:
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
    path: VirtualLane | None = _compute_path_through_crossing(ts, start_segment, turn_segment)
    if path is None:
        raise ValueError("Car specified a turn intent with invalid path.")

    horizontal_horizon = Interval(pos_on_segment, pos_on_segment + braking_dist)
    physical_segment_intervals: list[SegmentInterval] = compute_segment_intervals(ts, path, pos_on_segment, length)
    path_segment_intervals: list[SegmentInterval] = compute_segments_safety_envelope(
        ts,
        path,
        pos_on_segment,
        horizontal_horizon.length(),
        length
    )

    # If the turn intent exceeds what the car can see, we set the turn intent to the last lane segment.
    # For example, if the car turns left 1k units away but can only see 10 forward, the turn_segment gets useless.
    if turn_segment not in path.segments:
        end_lane: Segment = path.segments[-1]
        if not isinstance(end_lane, LaneSegment):
            raise ValueError("Path must end on a lane segment.")
        turn_segment = end_lane

    return path, physical_segment_intervals, path_segment_intervals, turn_segment, horizontal_horizon


def compute_parallel_virtual_lanes(
        ts: TrafficSnapshotReader,
        pos_on_segment: float,
        start_segment: LaneSegment,
        turn_segment: LaneSegment,
        path: VirtualLane,
        car_direction: Direction,
        horizon: Interval
) -> list[list[VirtualLaneNew]]:
    parallel_segments = compute_parallel_segments(ts, start_segment, turn_segment, path, car_direction)

    parallel_virtual_lanes: list[list[VirtualLaneNew]] = []
    for parallel_segment in parallel_segments:
        virtual_lanes: list[VirtualLaneNew] = []
        for segment_list in parallel_segment:
            virtual_lanes.append(segments_to_virtual_lane(pos_on_segment, segment_list, horizon, ts))
        parallel_virtual_lanes.append(virtual_lanes)

    return parallel_virtual_lanes


def segments_to_virtual_lane(pos_on_segment: float, segments: list[Segment], horizon: Interval, ts: TrafficSnapshotReader) -> VirtualLaneNew:
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
        path: VirtualLane,
        car_direction: Direction
) -> list[list[list[Segment]]]:
    through_crossing = any(map(lambda seg: not seg.is_lane_segment, path.segments))
    if through_crossing:
        lanes_connected_to_crossing = _compute_all_lanes_connected_to_crossing(ts, start_segment, car_direction)
        return _compute_segments_through_crossing(
            ts,
            start_segment,
            turn_segment,
            lanes_connected_to_crossing,
                                 path
        )
    else:
        # no crossing found
        parallel_lane_segments: list[LaneSegment] = compute_parallel_lane_segments(ts, start_segment)
        parallel_segments: list[list[Segment]] = []

        for parallel_lane_segment in parallel_lane_segments:
            parallel_segments.append([parallel_lane_segment])

        parallel_segments.sort(key=lambda lane: lane.segments[0].lane.lane_index)

        return [parallel_segments]


def _compute_all_lanes_connected_to_crossing(ts: TrafficSnapshotReader, start_segment: LaneSegment,
                                             car_direction: Direction) -> list[LaneSegment]:
    """"
    We want to find all lane segments that are connected to any crossing segment (or are connected to the crossing
    in the coarse path).
    """

    # find a crossing segment by "driving" in the car direction
    current_segment = start_segment
    while not current_segment.is_lane_segment:
        current_segment = ts.get_adjacent_segment(current_segment.uid, car_direction)
        if current_segment is None:
            raise ValueError("Car specified a turn intent with invalid path.")

    # we use BFS to find all lane segments that are connected to a crossing
    lanes_connected_to_crossing: list[LaneSegment] = []
    visited_segments = set()
    queue = deque([current_segment])
    visited_segments.add(current_segment.uid)

    while queue:
        segment = queue.popleft()

        for direction in Direction:
            neighbor: Segment | None = ts.get_adjacent_segment(segment.uid, direction)

            if neighbor is None or neighbor.uid in visited_segments:
                continue

            if isinstance(neighbor, LaneSegment):
                lanes_connected_to_crossing.append(neighbor)
                visited_segments.add(neighbor.uid)
            else:
                visited_segments.add(neighbor.uid)
                queue.append(neighbor)

    return lanes_connected_to_crossing

def _compute_segments_through_crossing(
        ts: TrafficSnapshotReader,
        start_segment: LaneSegment,
        turn_segment: LaneSegment,
        lanes_connected_to_crossing: list[LaneSegment],
        path: VirtualLane
) -> list[list[list[Segment]]]:
    start_parallel_segments: list[LaneSegment] = compute_parallel_lane_segments(ts, start_segment)
    turn_parallel_segments: list[LaneSegment] = compute_parallel_lane_segments(ts, turn_segment)

    lane_candidates: list[VirtualLane] = []
    for lane in start_parallel_segments:
        if lane == start_segment:
            continue

        for dest_lane in lanes_connected_to_crossing:
            if dest_lane not in turn_parallel_segments or dest_lane == turn_segment:
                continue

            opposing_lane: VirtualLane | None = _compute_path_through_crossing(ts, lane, dest_lane)
            if opposing_lane is not None:
                lane_candidates.append(opposing_lane)

        # create the placeholder
        if len(lane_candidates) == 0:
            lane_candidates.append(VirtualLane([lane]))

    total_parallel_segments: list[list[list[Segment]]] = []
    for lane_candidate in lane_candidates:
        parallel_segments: list[list[Segment]] = [
            lane_candidate.segments,
            path.segments
        ]
        parallel_segments.sort(key=lambda segments: segments[0].lane.lane_index)
        total_parallel_segments.append(parallel_segments)

    return total_parallel_segments


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
    if (turn_direction == TurnDirection.RIGHT and start_road_direction == RoadOrientation.HORIZONTAL) \
            or (turn_direction == TurnDirection.LEFT and start_road_direction == RoadOrientation.VERTICAL):
        segments_of_target_lane.reverse()

    for segment in segments_of_target_lane:
        pos = segment.get_position(ts)[segment_position_index]
        start_pos = start_coords[segment_position_index]

        match turn_direction:
            case TurnDirection.LEFT:
                if start_road_direction == RoadOrientation.HORIZONTAL:
                    if pos > start_pos:
                        return segment
                else:
                    if pos < start_pos:
                        return segment
            case TurnDirection.RIGHT:
                if start_road_direction == RoadOrientation.VERTICAL:
                    if pos > start_pos:
                        return segment
                else:
                    if pos < start_pos:
                        return segment
    raise ValueError("Turn intent not found.")


def _compute_path_through_crossing(
        ts: TrafficSnapshotReader,
        start: LaneSegment,
        end: LaneSegment
) -> VirtualLane | None:
    """"
    Computes the path from start to end through a crossing segment.
    Our path can have at most 1 direction change, therefore, we bruteforce where that change occurs.

    One can drastically improve the performance of this algorithm by carefully implementing BFS and computing the
    allowed directions (a list of most 2 directions) depending on the start and end segment.
    However, one has to be very careful implementing that, because we also care about the opposite paths.
    """
    if start == end:
        return VirtualLane([start])

    for direction_1 in Direction:
        path_1: list[Segment] = [start]
        current_seg_1: Segment = start

        # Follow Direction 1 as far as possible
        while True:
            if current_seg_1 == end:
                return VirtualLane(path_1)

            # Guess a direction change
            for direction_2 in Direction:
                if direction_2 == direction_1:
                    continue

                # we clone the paths and compute where we end up when using this direction
                path_2 = list(path_1)
                current_seg_2 = ts.get_adjacent_segment(current_seg_1.uid, direction_2)
                # todo: prevent traversing through lanes

                # Follow direction_2 as far as possible
                while current_seg_2 is not None:
                    path_2.append(current_seg_2)
                    if current_seg_2 == end:
                        return VirtualLane(path_2)

                    if current_seg_2 in path_1:
                        # this would be a loop
                        break
                    else:
                        current_seg_2 = ts.get_adjacent_segment(current_seg_2.uid, direction_2)

            # didn't work, go to the next segment in direction_1
            next_seg = ts.get_adjacent_segment(current_seg_1.uid, direction_1)
            if next_seg is None or next_seg in path_1:
                break
            current_seg_1 = next_seg
            path_1.append(current_seg_1)

    return None
