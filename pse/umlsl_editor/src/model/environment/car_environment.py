from enum import Enum

from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import (
    TrafficSnapshotReader,
)
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.model.environment.environment_helper import (
    compute_parallel_lane_segments,
)
from pse.umlsl_editor.src.model.environment.multi_view import (
    compute_parallel_virtual_lanes,
    compute_path,
)
from pse.umlsl_editor.src.model.environment.segment_intervals_helper import (
    compute_segments_safety_envelope,
)
from pse.umlsl_editor.src.model.errors.car_errors import CarValidationError
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import (
    LaneSegment,
)
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import (
    SegmentInterval,
)
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import (
    VirtualLane,
    VirtualLaneNew,
)
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import (
    TurnDirection,
    TurnIntent,
)


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


class CarEnvironment:
    """
    This class includes information on how the car interacts with the segments of the traffic snapshot.
    """
    turn_direction: TurnDirection | None

    # List of parallel virtual lanes.
    parallel_virtual_lanes: list[list[VirtualLaneNew]]
    # The path of the car which is a list of segments.
    path: list[Segment]
    # The path of the car where each segment is equipped with an interval.
    # This is analogous to the seg_V method in the paper if we assume the view occupies the entire map.
    # To access only the visible segments in a view, use the path_segments_in_view function in this class.
    physical_segment_intervals: list[SegmentInterval]
    # Splits the entire path into segments intervals.
    path_segment_intervals: list[SegmentInterval]

    horizontal_horizon: Interval

    reserved_lanes: list[SegmentInterval]
    reserved_crossings: list[SegmentInterval]
    reserved: list[SegmentInterval]
    claimed_lanes: list[SegmentInterval]
    claimed_crossings: list[SegmentInterval]
    claimed: list[SegmentInterval]

    def __init__(
            self,
            car_direction: Direction,
            turn_direction: TurnDirection,
            turn_segment: SegmentInterval,
            path: list[Segment],
            physical_segment_intervals: list[SegmentInterval],
            path_segment_intervals: list[SegmentInterval],
            horizontal_horizon: Interval,
            parallel_virtual_lanes: list[list[VirtualLaneNew]],
            reserved_segment_intervals: list[SegmentInterval],
            claimed_segment_intervals: list[SegmentInterval],
    ):
        self.car_direction = car_direction
        self.turn_direction = turn_direction
        self.turn_segment = turn_segment
        self.path = path
        self.physical_segment_intervals = physical_segment_intervals
        self.path_segment_intervals = path_segment_intervals
        self.horizontal_horizon = horizontal_horizon
        self.parallel_virtual_lanes = parallel_virtual_lanes

        self.reserved = reserved_segment_intervals
        self.reserved_lanes = list(filter(lambda seg: seg.segment.is_lane_segment, reserved_segment_intervals))
        self.reserved_crossings = list(filter(lambda seg: not seg.segment.is_lane_segment, reserved_segment_intervals))

        self.claimed = claimed_segment_intervals
        self.claimed_lanes = list(filter(lambda seg: seg.segment.is_lane_segment, claimed_segment_intervals))
        self.claimed_crossings = list(filter(lambda seg: not seg.segment.is_lane_segment, claimed_segment_intervals))

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
        car_direction = _compute_car_direction(speed, car_lane, road)

        turn_direction: TurnDirection = TurnDirection.STRAIGHT
        if turn_intent is None:
            # if the turn_intent is not specified, it means the car drives straight
            turn_intent = TurnIntent(TurnDirection.STRAIGHT, car_lane)
        else:
            turn_direction = turn_intent.direction

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

        path, physical_segment_intervals, path_segment_intervals, turn_segment, horizontal_horizon = compute_path(
            ts,
            length,
            start_segment,
            pos_on_segment,
            turn_intent,
            car_direction,
            settings_model.braking_distance()
        )

        reserved_segment_intervals: list[SegmentInterval] = compute_segments_safety_envelope(
            ts,
            path,
            pos_on_segment,
            length,
            car_params.length
        )
        claimed_segment_intervals: list[SegmentInterval] = _compute_claimed_envelope(
            reserved_segment_intervals,
            car_params.transition,
            ts
        )

        print("-------- car ", car_params.name)
        print("path is ", list(map(lambda seg: ts.get_segment_info(seg.uid), path)))
        print("path seg-intervals is ", list(
            map(lambda seg: ts.get_segment_info(seg.segment.uid) + " " + str(seg.interval), path_segment_intervals)))
        print("horizon is ", horizontal_horizon)
        print("physical segment intervals are ",
              list(
                  map(lambda seg: f"{ts.get_segment_info(seg.segment.uid)}{seg.interval}", physical_segment_intervals)))
        print("reserved segment intervals are ", list(
            map(lambda seg: f"{ts.get_segment_info(seg.segment.uid)}{seg.interval}", reserved_segment_intervals)))
        print("claimed segment intervals are ",
              list(map(lambda seg: f"{ts.get_segment_info(seg.segment.uid)}{seg.interval}", claimed_segment_intervals)))

        parallel_virtual_lanes: list[list[VirtualLaneNew]] = compute_parallel_virtual_lanes(
            ts,
            start_segment,
            turn_direction,
            turn_segment,
            path,
            horizontal_horizon
        )

        for parallel_virtual_lane in parallel_virtual_lanes:
            print("parallel virtual lane:")
            for virtual_lane in parallel_virtual_lane:
                print(" > virtual lane is ", list(map(lambda seg: ts.get_segment_info(seg.segment.uid) + " " + str(seg.interval), virtual_lane.segment_intervals)))

        return CarEnvironment(
            car_direction,
            turn_direction,
            SegmentInterval(turn_segment, Interval(0, turn_segment.get_size_in_direction(ts))),
            path,
            physical_segment_intervals,
            path_segment_intervals,
            horizontal_horizon,
            parallel_virtual_lanes,
            reserved_segment_intervals,
            claimed_segment_intervals
        )

    def translate_interval_coordinates(self, virtual_lanes: list[VirtualLaneNew], horizon: Interval, to_translate: list[SegmentInterval], translate_car: 'Car', ts: TrafficSnapshotReader) -> dict[Segment, Interval]:
        """"
        Translates the segment of the given interval into the coordinates of the "self" car - w.r.t the virtual_lanes.
        """

        # 1) for each element in to_translate, figure out the corresponding virtual lane that includes that segment -> create a map from to_translate to virtual_lane
        # 2) for each virtual lane, translate the interval into the coordinate system of the "self" car
        # 3) remove those segment intervals that do not intersect with the horizon of the "self" car

        lane_to_segment_intervals: dict[int, dict[Segment, Interval]] = {}
        segments_to_virtual_lane: dict[Segment, int] = {}
        for virtual_lane_index in virtual_lanes:
            for segment_interval in virtual_lane_index.segment_intervals:
                lane_index = virtual_lanes.index(virtual_lane_index)
                segments_to_virtual_lane[segment_interval.segment] = lane_index

        # 2) align intervals of to_translate
        self_dir: Direction = self.car_direction
        turn_dir: TurnDirection = self.turn_direction
        car_dir: Direction = translate_car.environment.car_direction
        swap_alignment = car_dir == self_dir.opposite

        if not swap_alignment and turn_dir != TurnDirection.STRAIGHT:
            # we have to be careful on turns
            swap_alignment = turn_dir == TurnDirection.LEFT and car_dir == Direction.DOWN or turn_dir == TurnDirection.RIGHT and car_dir == Direction.UP

        aligned_to_translate: list[SegmentInterval] = []
        if swap_alignment:
            for translate_segment_interval in to_translate:
                segment = translate_segment_interval.segment
                segment_length = segment.get_size_in_direction(ts)
                interval = translate_segment_interval.interval

                new_start = segment_length - interval.end
                new_end = segment_length - interval.start

                aligned_interval = Interval(new_start, new_end)
                aligned_to_translate.append(SegmentInterval(segment, aligned_interval))
        else:
            aligned_to_translate = to_translate

        for translate_segment_interval in aligned_to_translate:
            lane_index = segments_to_virtual_lane.get(translate_segment_interval.segment)
            if lane_index is not None:
                if lane_to_segment_intervals.get(lane_index) is None:
                    lane_to_segment_intervals[lane_index] = {}

                lane_to_segment_intervals[lane_index][translate_segment_interval.segment] = translate_segment_interval.interval

        translated_segment_intervals: dict[Segment, Interval] = {}
        for lane_index, virtual_lane in enumerate(virtual_lanes):
            segment_intervals_on_lane: dict[Segment, Interval] = lane_to_segment_intervals.get(lane_index)
            if segment_intervals_on_lane is None:
                continue

            offset = 0
            for lane_segment_interval in virtual_lane.segment_intervals:
                lane_segment = lane_segment_interval.segment

                interval = segment_intervals_on_lane.get(lane_segment)
                if interval is not None:
                    interval_on_lane = Interval(interval.start + offset, interval.end + offset)
                    if interval_on_lane.intersects(horizon):
                        translated_segment_intervals[lane_segment] = interval_on_lane

                offset += lane_segment.get_size_in_direction(ts)


        return translated_segment_intervals


def _compute_car_direction( speed: float, lane: Lane, road: Road) -> Direction:
    # compute car direction
    car_direction: Direction
    if road.orientation == RoadOrientation.HORIZONTAL:
        car_direction = Direction.LEFT if (speed < 0) else Direction.RIGHT
    else:
        car_direction = Direction.DOWN if (speed < 0) else Direction.UP
    if not lane.is_forward():
        car_direction = car_direction.opposite
    return car_direction


def _compute_claimed_envelope(reserved_segment_intervals: list[SegmentInterval], transition: float,
                              ts: TrafficSnapshotReader) -> list[SegmentInterval]:
    if transition == 0 or len(reserved_segment_intervals) != 1:
        return []

    segment_interval = reserved_segment_intervals[0]
    parallel_segments = compute_parallel_lane_segments(ts, segment_interval.segment)
    current_index = parallel_segments.index(segment_interval.segment)

    road = ts.get_road_by_uid(segment_interval.segment.lane.road_uid)
    delta = 1 if transition > 0 else -1
    if road.orientation == RoadOrientation.HORIZONTAL:
        delta = -delta

    # 1 means up/right, -1 means down/left. The segments are sorted by lane index which matches this mapping.
    claimed_segment_index = current_index + delta
    claimed_segment = parallel_segments[claimed_segment_index]

    return [SegmentInterval(claimed_segment, segment_interval.interval)]
