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
    def create_environment(
            ts: TrafficSnapshotReader,
            car_lane: Lane,
            pos_on_lane_center: float,
            car_size: float,
            speed: float,
            turn_intent: TurnIntent,
            settings_model: SettingsModel
    ) -> 'CarEnvironment':
        road_id = car_lane.road_uid
        road = ts.get_road_by_uid(road_id)
        pos_on_lane = pos_on_lane_center - car_size / 2  # we need the rear
        start_segment = ts.get_segment_from_lane_position(car_lane, pos_on_lane)

        # todo: extract into separate method
        if road.orientation == RoadOrientation.HORIZONTAL:
            car_direction = Direction.LEFT if speed < 0 else Direction.RIGHT
        else:
            car_direction = Direction.UP if speed > 0 else Direction.DOWN

        #  print("car_direction", car_direction)

        #  print("turn intent is ", turn_intent)

        if turn_intent is None:
            return CarEnvironment(VirtualLane([]), [], Interval(0.0, 0.0), [])
        if not isinstance(start_segment, LaneSegment):
            raise ValueError("Car must start on a lange segment")

        # converts the absolute position to the position on the start_segment
        pos_on_segment = pos_on_lane - start_segment.get_position(ts)[road.orientation.value]

        #  print("braking dist is", braking_distance)
        # print("car lane ", car_lane, " pos on seg: ", pos_on_segment, " start_segment ", start_segment, " car dir ", car_direction)
        # print("lane pos is ", lane_pos, " pos on seg: ", pos_on_segment, " direction is ", car_direction)

        turn_direction = turn_intent.direction

        turn_segment: LaneSegment = _find_turn_intent_segment(ts, start_segment, turn_intent, car_direction)
        path: VirtualLane | None = _compute_path_through_crossing(ts, start_segment, turn_segment, turn_direction)

        if path is None:
            return CarEnvironment(VirtualLane([]), [], Interval(0.0, 0.0), [])  # todo: <- remove
            raise ValueError("Car specified a turn intent with invalid path.")

        path_segment_intervals: list[SegmentInterval] = _compute_segment_intervals(ts, path, pos_on_segment, car_size)
        horizontal_horizon: Interval = compute_horizontal_horizon(
            path_segment_intervals,
            settings_model.braking_distance()
        )
        # compute the parallel segments of the start and turn segments in opposing driving direction
        start_opp_parallel_segments: list[LaneSegment] = _compute_opposing_parallel_segments(ts, start_segment)
        turn_opp_parallel_segments: list[LaneSegment] = _compute_opposing_parallel_segments(ts, turn_segment)

        opposing_parallel_virtual_lanes: list[list[VirtualLane]] = []
        for start_opp_parallel_segment in start_opp_parallel_segments:
            opposing_virtual_lanes: list[VirtualLane] = []

            for turn_opp_parallel_segment in turn_opp_parallel_segments:
                segments_through_crossing: list[Segment] | None = _compute_path_through_crossing(
                    ts,
                    start_opp_parallel_segment,
                    turn_opp_parallel_segment,
                    turn_direction
                )
                if segments_through_crossing is None:
                    raise ValueError("Cannot compute path of opposing parallel segments.")
                opposing_virtual_lanes.append(VirtualLane(segments_through_crossing))

            opposing_parallel_virtual_lanes.append(opposing_virtual_lanes)

        parallel_virtual_lanes: list[list[VirtualLane]] = []
        for opp_parallel_virtual_lanes in opposing_parallel_virtual_lanes:
            parallel_virtual_lane: list[VirtualLane] = [path]

            for opp_virtual_lane in opp_parallel_virtual_lanes:
                parallel_virtual_lane.append(opp_virtual_lane)

            parallel_virtual_lanes.append(parallel_virtual_lane)

        return CarEnvironment(
            path,
            path_segment_intervals,
            horizontal_horizon,
            parallel_virtual_lanes
        )


def _compute_opposing_parallel_segments(ts: TrafficSnapshotReader, segment: LaneSegment) -> list[LaneSegment]:
    opposing_direction = -segment.lane.get_direction()
    return list(
        filter(
            lambda seg: seg.lane.get_direction() == opposing_direction,
            _compute_parallel_lane_segments(ts, segment)
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
        while next_segment is not None and not next_segment.is_lane_segment:
            # if we start on a lane segment and move orthogonal to its driving direction, we cannot reach a crossing
            # segment
            assert isinstance(next_segment, LaneSegment)
            segments.append(next_segment)
            next_segment = ts.get_adjacent_segment(next_segment.uid, direction)

    segments.sort(key=lambda seg: seg.lane.lane_index)
    return segments


def _compute_path_straight(ts: TrafficSnapshotReader, car_direction: Direction, segment: Segment) -> VirtualLane:
    # todo: path is currently infinite. it must not exceed the horizontal horizon except for safety envelope after a crossing
    path = [segment]
    next_segment = ts.get_adjacent_segment(segment.uid, car_direction)
    while next_segment is not None:
        path.append(next_segment)
        next_segment = ts.get_adjacent_segment(next_segment.uid, car_direction)

    return VirtualLane(path)


def compute_horizontal_horizon(path_segment_intervals: list[SegmentInterval], braking_dist: float) -> Interval:
    """
    Computes the horizontal horizon of the car's path.
    It usually equals the (maximum) braking distance, so that every car can come ot a complete stand-still within
    the horizon. However, on crossings, the horizon is expanded until after the crossing.
    """

    virtual_pos: float = 0
    stopped_crossing_i: int = -1
    start = path_segment_intervals[0].interval.start

    for i, seg_interval in enumerate(path_segment_intervals):
        segment = seg_interval.segment
        interval = seg_interval.interval

        next_virtual_pos = virtual_pos + interval.length()

        if next_virtual_pos > braking_dist:
            if segment.is_lane_segment:
                # the car can come to a complete stand-still within the horizon
                return Interval(start, braking_dist)
            else:
                # car stops at crossing (segment with index i)
                stopped_crossing_i = i
                break

        virtual_pos = next_virtual_pos

    # we have to advance until after the crossing starting at index stopped_crossing_i
    for i in range(stopped_crossing_i + 1, len(path_segment_intervals)):
        seg_interval = path_segment_intervals[i]
        virtual_pos += seg_interval.interval.length()

        if seg_interval.segment.is_lane_segment:
            # the path_segment_intervals already guarantees the safety envelope after a crossing
            # (the algorithm uses the size of the car exactly if the car otherwise stops in a crossing)
            return Interval(start, virtual_pos)

    # not terminating here would mean the there segments_interval algorithm stops in a crossing
    # this is not the case
    raise ValueError("The algorithm stopped in a crossing")


def _find_turn_intent_segment(
        ts: TrafficSnapshotReader,
        start: Segment,
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
    start_pos = start.get_position(ts)
    start_pos_x = start_pos[0]
    start_pos_y = start_pos[1]
    # we need to find the target lane segment based on the turn intent

    # collect all segments of the target lane
    segments_of_target_lane: list[Segment] = []
    for segment in ts.all_segments():
        if segment is LaneSegment:
            lane_segment: LaneSegment = segment
            if lane_segment.lane == turn_intent.target_lane:
                segments_of_target_lane.append(segment)

    turn_direction = turn_intent.direction

    # if there is no crossing on the road (-> 1 lane segment), we can terminate directly
    if len(segments_of_target_lane) == 1:
        assert turn_direction == TurnDirection.STRAIGHT
        return segments_of_target_lane[0]

    # the segment_position_index is used to consider only the relevant coordinate of the segments_of_target_lane list
    # this is the segment_position_index corresponding to a car driving horizontally
    segment_position_index: int = 0 if turn_direction == TurnDirection.STRAIGHT else 1
    # we have to flip the index if the car is driving vertically
    if car_direction in {Direction.DOWN, Direction.UP}:
        segment_position_index = 1 - segment_position_index

    segments_of_target_lane.sort(key=lambda x: x.get_position(ts)[segment_position_index])
    if car_direction in {Direction.LEFT, Direction.DOWN}:
        segments_of_target_lane.reverse()

    for segment in segments_of_target_lane:
        pos = segment.get_position(ts)[segment_position_index]

        match car_direction:
            case Direction.RIGHT:
                if pos > start_pos_x:
                    return segment
            case Direction.LEFT:
                if pos < start_pos_x:
                    return segment
            case Direction.DOWN:
                if pos < start_pos_y:
                    return segment
            case Direction.UP:
                if pos > start_pos_y:
                    return segment
    return None


def _compute_path_through_crossing(
        ts: TrafficSnapshotReader,
        start: Segment,
        end: LaneSegment,
        turn_direction: TurnDirection
) -> list[Segment] | None:
    if start == end:
        return [start]
    pass


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
