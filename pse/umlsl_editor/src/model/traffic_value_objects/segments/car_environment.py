from collections import deque
from enum import Enum

from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
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
    path_segment_intervals: list[SegmentInterval]

    horizontal_horizon: Interval

    reserved_lanes: list[SegmentInterval]
    reserved_crossings: list[CrossingSegment]
    claimed_lanes: list[SegmentInterval]
    claimed_crossings: list[CrossingSegment]

    def __init__(
            self,
            path: VirtualLane,
            path_segment_intervals: list[SegmentInterval],
            horizontal_horizon: Interval,
            parallel_virtual_lanes: list[list[VirtualLane]],
    ):
        self.path = path
        self.path_segment_intervals = path_segment_intervals
        self.horizontal_horizon = horizontal_horizon
        self.parallel_virtual_lanes = parallel_virtual_lanes

    def path_segments_in_view(self, view: View) -> list[SegmentInterval]:
        # collect visible segments in the view
        visible_segments: list[Segment] = []
        for lane in view.virtual_lanes:
            for segment in lane.segments:
                visible_segments.append(segment)

        # for each path_segment_interval we have to check if it is visible
        return list(filter(
            lambda path_seg_interval: path_seg_interval.segment in visible_segments,
            self.path_segment_intervals
        ))

    @staticmethod
    def validate_environment(
            ts: TrafficSnapshotReader,
            car_params: "CarParams",
            settings_model: SettingsModel
    ) -> str | None:
        # todo: validate car does not require reserving/claiming occupied segments
        # todo: validate car is not defined on a crossing
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
        length: float = car_params.length

        ts.debug_get_segments().clear()
        road = ts.get_road_by_uid(car_lane.road_uid)

        # compute car direction
        car_direction: Direction
        if road.orientation == RoadOrientation.HORIZONTAL:
            car_direction = Direction.LEFT if speed < 0 else Direction.RIGHT
        else:
            car_direction = Direction.UP if speed > 0 else Direction.DOWN

        if turn_intent is None:
            # if the turn_intent is not specified, it means the car drives straight
            turn_intent = TurnIntent(TurnDirection.STRAIGHT, car_lane)

        pos_on_lane_center: float = car_params.position_on_lane
        pos_on_lane = pos_on_lane_center - car_params.length / 2  # we need the rear
        start_segment = ts.get_segment_from_lane_position(car_params.lane, pos_on_lane)
        if not isinstance(start_segment, LaneSegment):
            raise ValueError("Car must start on a lange segment")

        path, path_segment_intervals, turn_segment, horizontal_horizon = _compute_path(
            ts,
            car_params,
            start_segment,
            pos_on_lane,
            turn_intent,
            car_direction,
            settings_model.braking_distance()
        )

        # add path to debug segments
        for seg in path.segments:
            ts.debug_get_segments()[seg.uid] = seg

        parallel_virtual_lanes: list[list[VirtualLane]] = _compute_parallel_virtual_lanes(
            ts,
            start_segment,
            turn_segment,
            path
        )
        return CarEnvironment(path, path_segment_intervals, horizontal_horizon, parallel_virtual_lanes)

def _compute_path(
        ts: TrafficSnapshotReader,
        car_params: "CarParams",
        start_segment: LaneSegment,
        pos_on_lane: float,
        turn_intent: TurnIntent,
        car_direction: Direction,
        braking_dist: float
) -> tuple[VirtualLane, list[SegmentInterval], LaneSegment, Interval]:
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

    # converts the absolute position to the position on the start_segment
    road = ts.get_road_by_uid(car_params.lane.road_uid)
    pos_on_segment = pos_on_lane - start_segment.get_position(ts)[road.orientation.value]

    turn_segment: LaneSegment = _find_turn_intent_segment(ts, start_segment, turn_intent, car_direction)
    unbounded_path: VirtualLane | None = _compute_path_through_crossing(ts, start_segment, turn_segment)

    if unbounded_path is None:
        raise ValueError("Car specified a turn intent with invalid path.")

    horizontal_horizon: Interval = compute_horizontal_horizon(
        ts,
        unbounded_path.segments,
        pos_on_segment,
        braking_dist
    )

    # take only those segments in the path within in the horizontal horizon
    path_segments: list[Segment] = []
    virtual_pos: float = 0
    for segment in unbounded_path.segments:
        size = segment.get_size_in_direction(ts)

        if virtual_pos > horizontal_horizon.end:
            break

        path_segments.append(segment)
        virtual_pos += size

    print("path is ", list(map(lambda seg: ts.get_segment_info(seg.uid), path_segments)))
    path = VirtualLane(path_segments)
    path_segment_intervals: list[SegmentInterval] = _compute_segment_intervals(ts, path, pos_on_segment, car_params.length)

    return path, path_segment_intervals, turn_segment, horizontal_horizon


def _compute_parallel_virtual_lanes(
        ts: TrafficSnapshotReader,
        start_segment: LaneSegment,
        turn_segment: LaneSegment,
        path: VirtualLane
) -> list[list[VirtualLane]]:
    # compute the parallel segments of the start and turn segments in opposing driving direction
    start_opp_parallel_segments: list[LaneSegment] = _compute_opposing_parallel_segments(ts, start_segment)
    turn_opp_parallel_segments: list[LaneSegment] = _compute_opposing_parallel_segments(ts, turn_segment)

    opposing_parallel_virtual_lanes: list[list[VirtualLane]] = []
    for start_opp_parallel_segment in start_opp_parallel_segments:
        opposing_virtual_lanes: list[VirtualLane] = []

        for turn_opp_parallel_segment in turn_opp_parallel_segments:
            segments_through_crossing: VirtualLane | None = _compute_path_through_crossing(
                ts,
                start_opp_parallel_segment,
                turn_opp_parallel_segment
            )
            if segments_through_crossing is None:
                raise ValueError("Cannot compute path of opposing parallel segments.")
            opposing_virtual_lanes.append(segments_through_crossing)

        opposing_parallel_virtual_lanes.append(opposing_virtual_lanes)

    parallel_virtual_lanes: list[list[VirtualLane]] = []
    for opp_parallel_virtual_lanes in opposing_parallel_virtual_lanes:
        parallel_virtual_lane: list[VirtualLane] = [path]

        for opp_virtual_lane in opp_parallel_virtual_lanes:
            parallel_virtual_lane.append(opp_virtual_lane)

        parallel_virtual_lanes.append(parallel_virtual_lane)

    print("--------")
    for parallel_virtual_lane in parallel_virtual_lanes:
        print("parallel virtual lane:")
        for virtual_lane in parallel_virtual_lane:
            print(" > virtual lane is ", list(map(lambda seg: ts.get_segment_info(seg.uid), virtual_lane.segments)))

    return parallel_virtual_lanes



def _compute_opposing_parallel_segments(ts: TrafficSnapshotReader, segment: LaneSegment) -> list[LaneSegment]:
    opposing_direction = -segment.lane.get_direction()
    parallel_lane_segments: list[LaneSegment] = _compute_parallel_lane_segments(ts, segment)

    return list(
        filter(
            lambda seg: seg.lane.get_direction() == opposing_direction,
            parallel_lane_segments
        )
    )


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

    segments: list[LaneSegment] = []
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


def compute_horizontal_horizon(
        ts: TrafficSnapshotReader,
        segments: list[Segment],
        pos_on_segment: float,
        braking_dist: float
) -> Interval:
    """
    Computes the horizontal horizon of the car's path.
    It usually equals the (maximum) braking distance, so that every car can come ot a complete stand-still within
    the horizon. However, on crossings, the horizon is expanded until after the crossing.
    """
    stopped_crossing_i: int = -1
    virtual_pos: float = pos_on_segment
    braking_pos = pos_on_segment + braking_dist

    for i, seg_interval in enumerate(segments):
        segment = segments[i]
        segment_size = segment.get_size_in_direction(ts)
        # we have to compute the remaining size on the car's segment
        # in the first iteration, we need to add the remaining size, otherwise the whole segment
        size_advancement = (segment_size - pos_on_segment) if i == 0 else segment_size

        virtual_pos += size_advancement

        if virtual_pos > braking_pos:
            if segment.is_lane_segment:
                # the car can come to a complete stand-still within the horizon
                return Interval(pos_on_segment, braking_pos)
            else:
                # car stops at crossing (segment with index i)
                stopped_crossing_i = i
                break

    # the car did not reach the braking distance before the crossing
    if stopped_crossing_i == -1:
        return Interval(pos_on_segment, braking_pos)

    # we have to advance until after the crossing starting at index stopped_crossing_i
    for i in range(stopped_crossing_i + 1, len(segments)):
        segment = segments[i]
        virtual_pos += segment.get_size_in_direction(ts)

        if segment.is_lane_segment:
            # the path_segment_intervals already guarantees the safety envelope after a crossing
            # (the algorithm uses the size of the car exactly if the car otherwise stops in a crossing)
            return Interval(pos_on_segment, virtual_pos)

    # not terminating here would mean the there segments_interval algorithm stops in a crossing
    # this is not the case
    raise ValueError("The algorithm stopped in a crossing")


def _find_turn_intent_segment(
        ts: TrafficSnapshotReader,
        start: LaneSegment,
        turn_intent: TurnIntent,
        car_direction: Direction
) -> LaneSegment | None:
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
        while next_segment is not None:
            next_segment = ts.get_adjacent_segment(next_segment.uid, car_direction)
            if isinstance(next_segment, LaneSegment):
                return next_segment

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
    return None


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
    interval_start_offset = pos_on_segment

    # debug: print("start at", interval_start_offset, " car size is ", car_size)

    result = []
    next_size = car_size

    i = 0
    while next_size > 0:
        current_size = next_size
        seg_i = path.segments[i]

        b_i: float
        if seg_i.is_lane_segment:
            # debug: print((interval_start_offset + current_size, seg_i.get_size_in_direction(ts)))
            b_i = min(interval_start_offset + current_size, seg_i.get_size_in_direction(ts))
        else:
            b_i = seg_i.get_size_in_direction(ts)
            # During crossing segments, the car_size is not used.
            # However, if the car exists the crossing segments, it should see as least its own size.
            next_size = max(next_size, car_size)

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
