from enum import Enum

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

    reserved_lanes: list[SegmentInterval]
    reserved_crossings: list[CrossingSegment]
    claimed_lanes: list[SegmentInterval]
    claimed_crossings: list[CrossingSegment]

    space_interval: Interval
    """"
    max_v = self._traffic_snapshot.get_max_velocity()
    horizon = max_v * max_v / (2.0 * braking_accel)
    horizontal_extension = Interval(
        car.absolute_position() - horizon,
        car.absolute_position() + horizon
    )
    """

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
    def empty():
        return CarEnvironment()

    @staticmethod
    def create_environment(
            ts: TrafficSnapshotReader,
            car_lane: Lane,
            pos_on_lane_center: float,
            car_size: float,
            speed: float,
            turn_intent: TurnIntent
    ) -> 'CarEnvironment':
        road_id = car_lane.road_uid
        road = ts.get_road_by_uid(road_id)
        pos_on_lane = pos_on_lane_center - car_size / 2 # we need the rear
        segment = ts.get_segment_from_lane_position(car_lane, pos_on_lane)

        # todo: extract into separate method
        if road.orientation == RoadOrientation.HORIZONTAL:
            car_direction = Direction.LEFT if speed < 0 else Direction.RIGHT
        else:
            car_direction = Direction.UP if speed > 0 else Direction.DOWN

      #  print("car_direction", car_direction)

      #  print("turn intent is ", turn_intent)

        if turn_intent is None:
            return CarEnvironment()
        if segment is None and segment is not LaneSegment:
            raise ValueError("Segment is None or not a LaneSegment")

        pos_on_segment = pos_on_lane - segment.get_position(ts)[road.orientation.value]



       # print("car lane ", car_lane, " pos on seg: ", pos_on_segment, " segment ", segment, " car dir ", car_direction)
        lane_pos = car_lane.get_one_dimensional_position(ts)
       # print("lane pos is ", lane_pos, " pos on seg: ", pos_on_segment, " direction is ", car_direction)

        turn_direction = turn_intent.direction

        if turn_direction == TurnDirection.STRAIGHT:
            path = _compute_path_straight(ts, car_direction, segment)
            path_segs = list(map(lambda x: ts.get_segment_info(x.uid), path.segments))
            path_segment_intervals = _compute_segment_intervals(ts, path, pos_on_segment, car_size)
          #  print("path is ", path)
          #  print("path segments are ", path_segs)
            segment_intervals_text = list(map(lambda x: f"{ts.get_segment_info(x.segment.uid)}{x.interval}", path_segment_intervals))
         #   print("segment intervals are ", segment_intervals_text)

            target_segment =_find_turn_intent_segment(ts, segment, turn_intent, car_direction)
           # print("target segment is ", ts.get_segment_info(target_segment.uid) if target_segment is not None else "None")
            return CarEnvironment()
        else:
            # todo
            return CarEnvironment()
        #  visible_segments = _compute_visible_segments(traffic_snapshot, path, pos, car_size)


def _compute_path_straight(ts: TrafficSnapshotReader, car_direction: Direction, segment: Segment) -> VirtualLane:
    # todo: path is currently infinite. it must not exceed the horizontal horizon except for safety envelope after a crossing
    path = [segment]
    next_segment = ts.get_adjacent_segment(segment.uid, car_direction)
    while next_segment is not None:
        path.append(next_segment)
        next_segment = ts.get_adjacent_segment(next_segment.uid, car_direction)

    return VirtualLane(path)

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
        start: LaneSegment,
        end: LaneSegment,
        turn_direction: TurnDirection
) -> list[Segment] | None:

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
