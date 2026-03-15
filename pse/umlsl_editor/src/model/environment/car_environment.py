from collections import deque
from enum import Enum
from typing import Tuple

from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.environment.environment_helper import compute_parallel_lane_segments
from pse.umlsl_editor.src.model.environment.multi_view import compute_parallel_virtual_lanes, compute_path
from pse.umlsl_editor.src.model.environment.segment_intervals_helper import compute_segment_intervals, \
    compute_segments_safety_envelope
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

        print("--------")
        print("path is ", list(map(lambda seg: ts.get_segment_info(seg.uid), path.segments)))
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

        parallel_virtual_lanes: list[list[VirtualLane]] = compute_parallel_virtual_lanes(
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
    parallel_segments = compute_parallel_lane_segments(ts, segment_interval.segment)
    current_index = parallel_segments.index(segment_interval.segment)
    claimed_segment_index = current_index + 1 if transition > 0 else current_index - 1
    claimed_segment = parallel_segments[claimed_segment_index]

    return [SegmentInterval(claimed_segment, segment_interval.interval)]
