from collections import deque
from enum import Enum
from typing import Tuple

from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.errors.car_errors import CarValidationError
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import VirtualLane, Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection, TurnIntent
from pse.umlsl_editor.src.query.view import View


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class CarEnvironment:
    """
    This class includes information on how the car interacts with the segments of the traffic snapshot.
    """

    # List of parallel virtual lanes.
    parallel_virtual_lanes: list[list[VirtualLane]]
    # The path of the car which is a list of segments.
    path: VirtualLane
    # The path of the car where each segment is equipped with an interval.
    # This is analogous to the seg_V method in the paper if we assume the view occupies the entire map.
    # To access only the visible segments in a view, use the path_segments_in_view function in this class.
    physical_segment_intervals: list[SegmentInterval]
    # Splits the entire path into segments intervals.
    path_segment_intervals: list[SegmentInterval]

    horizontal_horizon: Interval

    reserved_lanes: list[SegmentInterval]
    reserved_crossings: list[SegmentInterval]
    claimed_lanes: list[SegmentInterval]
    claimed_crossings: list[SegmentInterval]

    def __init__(
            self,
            path: VirtualLane,
            physical_segment_intervals: list[SegmentInterval],
            path_segment_intervals: list[SegmentInterval],
            horizontal_horizon: Interval,
            parallel_virtual_lanes: list[list[VirtualLane]],
            reserved_segment_intervals: list[SegmentInterval],
            claimed_segment_intervals: list[SegmentInterval],
    ):
        self.path = path
        self.physical_segment_intervals = physical_segment_intervals
        self.path_segment_intervals = path_segment_intervals
        self.horizontal_horizon = horizontal_horizon
        self.parallel_virtual_lanes = parallel_virtual_lanes

        self.reserved_lanes = list(filter(lambda seg: seg.segment.is_lane_segment, reserved_segment_intervals))
        self.reserved_crossings = list(filter(lambda seg: not seg.segment.is_lane_segment, reserved_segment_intervals))

        self.claimed_lanes = list(filter(lambda seg: seg.segment.is_lane_segment, claimed_segment_intervals))
        self.claimed_crossings = list(filter(lambda seg: not seg.segment.is_lane_segment, claimed_segment_intervals))

    def _visible_segments_in_view(self, view: View) -> list[tuple[Segment, Interval, Interval]]:
        # collect visible segments in the view
        visible_segments: list[Segment] = []
        for virtual_lane in view.virtual_lanes:
            visible_segments.extend(virtual_lane.segments)

        physical_visible_segments = []

        if len(self.physical_segment_intervals) == 0:
            return []

        horizon = view.horizon

        start_segment = self.physical_segment_intervals[0].segment
        # If the horizon ranges over multiple segments and eventually reaches the physical segments occupied by this
        # car, we have to compute the correct offset when checking whether the segments of this car intersect the horizon.
        #
        # For instance, consider ego with horizon that ranges over 'lane1 - crossing1 - crossing2 - lane2', with
        # driving direction left to right, where "this" car is placed on lane2 directly after crossing2.
        # Since ego is placed rather at the end of lane1 (we consider a horizon that ranges over the crossing), a realistic horizon
        # may be [100, 150] (the start of the interval is relative to the start of lane1).
        # However, when considering the physically occupied segments of "this" car, they may be [1, 10] (indicating
        # that the car is placed on lane2 with a starting offset of 1 on lane2).
        # When computing the intersection, we have to shift the physically occupied segments of "this" car by an offset
        # that is computed by iterating through the path of ego and collecting the lengths until the segment lane2 is reached.
        next_start = self.physical_segment_intervals[0].interval.start
        for i, path_segment_interval in enumerate(view.car.environment.path_segment_intervals):
            segment = path_segment_interval.segment
            interval = path_segment_interval.interval

            if segment.uid == start_segment.uid:
                break
            else:
                if i == 0:
                    next_start += interval.start

                next_start += interval.length()

        for physical_segment_interval in self.physical_segment_intervals:
            interval = physical_segment_interval.interval
            segment_length = interval.length()

            abs_pos_interval = Interval(next_start, next_start + segment_length)

            # check if segment_interval intersects horizon
            if horizon.intersects(abs_pos_interval):
                # we only consider those that are inside the view
                if physical_segment_interval.segment in visible_segments:
                    physical_visible_segments.append((physical_segment_interval.segment, interval, abs_pos_interval))

            next_start += segment_length

        return physical_visible_segments

    def visible_segments_in_view_abs_intervals(self, view: View) -> list[SegmentInterval]:
        segments = self._visible_segments_in_view(view)
        abs_segment_intervals = []
        for segment, interval, abs_interval in segments:
            abs_segment_intervals.append(SegmentInterval(segment, abs_interval))
        return abs_segment_intervals

    def visible_segments_in_view(self, view: View) -> list[SegmentInterval]:
        segments = self._visible_segments_in_view(view)
        abs_segment_intervals = []
        for segment, interval, abs_interval in segments:
            abs_segment_intervals.append(SegmentInterval(segment, interval))
        return abs_segment_intervals

    @staticmethod
    def validate_environment(
            ts: TrafficSnapshotReader,
            car: "Car",
            settings_model: SettingsModel
    ) -> str | None:
        pos_on_lane = car.position_on_lane  # rear of the car
        start_segment = ts.get_segment_from_lane_position(car.lane, pos_on_lane)
        if not isinstance(start_segment, LaneSegment):
            return "Car must start on a lane segment"
        return None

    @staticmethod
    def create_environment(
            ts: TrafficSnapshotReader,
            car_params: "CarParams",
            settings_model: SettingsModel
    ) -> 'CarEnvironment':
        car_lane: Lane = car_params.lane
        speed: float = car_params.speed
        turn_intent: TurnIntent = car_params.next_turn

        # ts.debug_get_segments().clear()
        road = ts.get_road_by_uid(car_lane.road_uid)

        length = car_params.get_braking_dist(settings_model.braking_acceleration)

        # compute car direction
        car_direction: Direction
        if road.orientation == RoadOrientation.HORIZONTAL:
            car_direction = Direction.LEFT if (speed < 0) else Direction.RIGHT
        else:
            car_direction = Direction.DOWN if (speed < 0) else Direction.UP
        if not car_lane.is_forward():
            car_direction = car_direction.opposite

        if turn_intent is None:
            # if the turn_intent is not specified, it means the car drives straight
            turn_intent = TurnIntent(TurnDirection.STRAIGHT, car_lane)

        pos_on_lane = car_params.position_on_lane  # rear of the car
        start_segment = ts.get_segment_from_lane_position(car_params.lane, pos_on_lane)
        if not isinstance(start_segment, LaneSegment):
            raise CarValidationError(content="Car must start on a lange segment")

        # converts the absolute position to the position on the start_segment
        road = ts.get_road_by_uid(car_params.lane.road_uid)
        segment_start_pos = start_segment.get_position(ts)[road.orientation.value]

        pos_on_segment: float
        match car_direction:
            case Direction.RIGHT:
                pos_on_segment = pos_on_lane - segment_start_pos
            case Direction.LEFT:
                pos_on_segment = start_segment.get_size_in_direction(ts) - (pos_on_lane - segment_start_pos)
            case Direction.UP:
                pos_on_segment = start_segment.get_size_in_direction(ts) - (segment_start_pos - pos_on_lane)
            case Direction.DOWN:
                pos_on_segment = segment_start_pos - pos_on_lane
            case _:
                raise ValueError(f"Car direction {car_direction} is not supported.")

        path, physical_segment_intervals, path_segment_intervals, turn_segment, horizontal_horizon = _compute_path(
            ts,
            length,
            start_segment,
            pos_on_segment,
            turn_intent,
            car_direction,
            settings_model.braking_distance()
        )

        reserved_segment_intervals: list[SegmentInterval] = _compute_segments_safety_envelope(
            ts,
            path,
            pos_on_segment,
            length,
            car_params.length
        )
        claimed_segment_intervals: list[SegmentInterval] = _compute_claimed_envelope(reserved_segment_intervals,
                                                                                     car_params.transition, ts)
        # reserved_segments = list(map(lambda seg_interval: seg_interval.segment, reserved_segment_intervals))
        # claimed_segment_intervals: list[SegmentInterval] = _compute_segments_safety_envelope(
        #             ts,
        #             path,
        #             pos_on_segment,
        #             settings_model.braking_distance(),
        #             length
        #         )
        #         claimed_segment_intervals = list(
        #             filter(lambda seg_interval: seg_interval.segment not in reserved_segments, claimed_segment_intervals))

        # todo: include transitions

        print("--------")
        print("path is ", list(map(lambda seg: ts.get_segment_info(seg.uid), path.segments)))
        print("horizon is ", horizontal_horizon)
        print("physical segment intervals are ",
              list(
                  map(lambda seg: f"{ts.get_segment_info(seg.segment.uid)}{seg.interval}", physical_segment_intervals)))
        print("reserved segment intervals are ", list(
            map(lambda seg: f"{ts.get_segment_info(seg.segment.uid)}{seg.interval}", reserved_segment_intervals)))
        print("claimed segment intervals are ",
              list(map(lambda seg: f"{ts.get_segment_info(seg.segment.uid)}{seg.interval}", claimed_segment_intervals)))

        # add path to debug segments
        # for seg in path.segments:
        #    ts.debug_get_segments()[seg.uid] = seg

        parallel_virtual_lanes: list[list[VirtualLane]] = _compute_parallel_virtual_lanes(
            ts,
            start_segment,
            turn_segment,
            path,
            car_direction
        )
        for parallel_virtual_lane in parallel_virtual_lanes:
            print("parallel virtual lane:")
            for virtual_lane in parallel_virtual_lane:
                print(" > virtual lane is ", list(map(lambda seg: ts.get_segment_info(seg.uid), virtual_lane.segments)))
        return CarEnvironment(
            path,
            physical_segment_intervals,
            path_segment_intervals,
            horizontal_horizon,
            parallel_virtual_lanes,
            reserved_segment_intervals,
            claimed_segment_intervals
        )


def _compute_claimed_envelope(reserved_segment_intervals: list[SegmentInterval], transition: float,
                              ts: TrafficSnapshotReader) -> list[SegmentInterval]:
    if transition == 0 or len(reserved_segment_intervals) != 1:
        return []

    segment_interval = reserved_segment_intervals[0]
    parallel_segments = _compute_parallel_lane_segments(ts, segment_interval.segment)
    current_index = parallel_segments.index(segment_interval.segment)
    claimed_segment_index = current_index + 1 if transition > 0 else current_index - 1
    claimed_segment = parallel_segments[claimed_segment_index]

    return [SegmentInterval(claimed_segment, segment_interval.interval)]


def _compute_path(
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

    braking_pos = pos_on_segment + braking_dist
    horizontal_horizon = Interval(pos_on_segment, braking_pos)

    physical_segment_intervals: list[SegmentInterval] = _compute_segment_intervals(ts, path, pos_on_segment, length)
    path_segment_intervals: list[SegmentInterval] = _compute_segments_safety_envelope(
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


def _compute_parallel_virtual_lanes(
        ts: TrafficSnapshotReader,
        start_segment: LaneSegment,
        turn_segment: LaneSegment,
        path: VirtualLane,
        car_direction: Direction
) -> list[list[VirtualLane]]:
    through_crossing = any(map(lambda seg: not seg.is_lane_segment, path.segments))
    if through_crossing:
        lanes_connected_to_crossing = _compute_all_lanes_connected_to_crossing(ts, start_segment, car_direction)
        return _compute_parallel_virtual_lanes_crossing(ts, start_segment, turn_segment, lanes_connected_to_crossing,
                                                        path)
    else:
        # no crossing found
        parallel_lane_segments: list[LaneSegment] = _compute_parallel_lane_segments(ts, start_segment)
        virtual_lanes: list[VirtualLane] = []

        for parallel_lane_segment in parallel_lane_segments:
            virtual_lanes.append(VirtualLane([parallel_lane_segment]))

        virtual_lanes.sort(key=lambda lane: lane.segments[0].lane.lane_index)

        return [virtual_lanes]


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


def _compute_parallel_virtual_lanes_crossing(
        ts: TrafficSnapshotReader,
        start_segment: LaneSegment,
        turn_segment: LaneSegment,
        lanes_connected_to_crossing: list[LaneSegment],
        path: VirtualLane
) -> list[list[VirtualLane]]:
    parallel_lane_segments: list[LaneSegment] = _compute_parallel_lane_segments(ts, start_segment)
    opposite_lane_segments: list[LaneSegment] = _compute_parallel_lane_segments(ts, turn_segment)

    lane_candidates: list[VirtualLane] = []
    for lane in parallel_lane_segments:
        if lane.uid == start_segment.uid:
            lane_candidates.append(path)
        else:
            for dest_lane in lanes_connected_to_crossing:
                if dest_lane not in opposite_lane_segments:
                    continue

                opposing_lane: VirtualLane | None
                is_forward = lane.lane.get_direction() == start_segment.lane.get_direction()
                if is_forward:
                    opposing_lane = _compute_path_through_crossing(ts, lane, dest_lane)
                else:
                    # for opposing paths we have to go from the intersection to the start
                    opposing_lane = _compute_path_through_crossing(ts, dest_lane, lane)

                if opposing_lane is not None:
                    lane_candidates.append(opposing_lane)

        # create the placeholder
        if len(lane_candidates) == 0:
            lane_candidates.append(VirtualLane([lane]))

    parallel_virtual_lanes: list[list[VirtualLane]] = []
    for lane_candidate in lane_candidates:
        parallel_virtual_lane: list[VirtualLane] = [lane_candidate, path]
        parallel_virtual_lane.sort(key=lambda vl: vl.segments[0].lane.lane_index)
        parallel_virtual_lanes.append(parallel_virtual_lane)

    return parallel_virtual_lanes


def _compute_parallel_lane_segments(ts: TrafficSnapshotReader, segment: LaneSegment) -> list[LaneSegment]:
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


def _compute_segment_intervals(
        ts: TrafficSnapshotReader,
        path: VirtualLane,
        pos_on_segment: float,
        car_size: float
) -> list[SegmentInterval]:
    """"
    This algorithm computes the real space a car occupies on a path.
    It is similar to the "Algorithm 2" (seg_V) method in the paper, however, the algorithm in the paper collects
    only those segments that are inside a given View.
    For performance and implementation reasons, we collect all these segment intervals when a car is created and later
    - during query evaluation - only take the relevant ones from this list that are inside the current View.
    """
    interval_start_offset = pos_on_segment

    result = []
    next_size = car_size

    i = 0
    while next_size > 0:
        current_size = next_size

        if i >= len(path.segments):
            return result

        seg_i = path.segments[i]

        b_i: float
        if seg_i.is_lane_segment:
            b_i = min(interval_start_offset + current_size, seg_i.get_size_in_direction(ts))
        else:
            b_i = seg_i.get_size_in_direction(ts)

        interval = Interval(interval_start_offset, b_i)
        next_size = current_size - interval.length()

        if next_size > 0:
            interval_start_offset = 0

        result.append(SegmentInterval(seg_i, interval))
        i += 1

    return result


def _compute_segments_safety_envelope(
        ts: TrafficSnapshotReader,
        path: VirtualLane,
        pos_on_segment: float,
        horizon_size: float,
        car_size: float
) -> list[SegmentInterval]:
    """"
    Computes the segment intervals of the car's path but expands over crossings and includes a safety envelope.
    The algorithm stops when the car reaches the horizon_size.

    If the car ends in a crossing, we make sure the segment_intervals are expanded until after the crossing.
    In this case, the last interval equals [0, car_size] to guarantee the safety envelope.
    """
    interval_start_offset = pos_on_segment

    result = []
    next_size = horizon_size

    i = 0
    while next_size > 0:
        current_size = next_size

        # since the input size can be arbitrarily large, we need to check if we reached the end of the path
        # unlike in the segment_intervals method, it is not guaranteed that the car reaches the end of the path
        if i >= len(path.segments):
            return result

        seg_i = path.segments[i]

        b_i: float
        if seg_i.is_lane_segment:
            # debug: print((interval_start_offset + current_size, seg_i.get_size_in_direction(ts)))
            b_i = min(interval_start_offset + current_size, seg_i.get_size_in_direction(ts))
        else:
            b_i = seg_i.get_size_in_direction(ts)
            # However, if the car exists the crossing segments, it must occupy its own size
            next_size = max(current_size, car_size)

        interval = Interval(interval_start_offset, b_i)
        # debug: print("interval:",interval)
        # without this check, the algorithm would stop in a crossing
        if seg_i.is_lane_segment:
            next_size = current_size - interval.length()

        if next_size > 0:
            interval_start_offset = 0

        result.append(SegmentInterval(seg_i, interval))
        i += 1

    return result
