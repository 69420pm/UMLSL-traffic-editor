from itertools import product

from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.environment.car_environment import CarEnvironment
from pse.umlsl_editor.src.model.environment.helper.segment_intervals_helper import compute_segment_intervals, \
    compute_segments_safety_envelope
from pse.umlsl_editor.src.model.environment.helper.segment_topology_helper import compute_path_through_crossing, \
    compute_parallel_lane_segments
from pse.umlsl_editor.src.model.environment.helper.turn_intent_helper import find_turn_intent_segment
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import VirtualLane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection, TurnIntent


class EnvironmentCreation:
    def __init__(self, ts: TrafficSnapshotReader, car_params: "CarParams", settings: SettingsModel):
        self.ts = ts
        self.car_params = car_params
        self.settings = settings

        self.lane = self.car_params.lane
        self.road = self.ts.get_road_by_uid(self.lane.road_uid)

        self.pos_on_lane = self.car_params.position_on_lane  # rear of the car
        start_segment = self.ts.get_segment_from_lane_position(self.car_params.lane, self.pos_on_lane)
        if start_segment is None or not isinstance(start_segment, LaneSegment):
            raise ValueError("Car must start on a lane segment.")
        self.start_segment = start_segment

        self.car_direction = self._compute_car_direction()
        self.pos_on_segment = self._compute_pos_on_segment()

        if car_params.next_turn is None:
            # if the turn_intent is not specified, it means the car drives straight
            self.specified_turn_intent = TurnIntent(TurnDirection.STRAIGHT, car_params.lane)
            self.specified_turn_direction = TurnDirection.STRAIGHT
        else:
            self.specified_turn_intent = car_params.next_turn
            self.specified_turn_direction = car_params.next_turn.direction

    def _compute_car_direction(self) -> Direction:
        speed = self.car_params.speed

        car_direction: Direction
        if self.road.orientation == RoadOrientation.HORIZONTAL:
            car_direction = Direction.LEFT if (speed < 0) else Direction.RIGHT
        else:
            car_direction = Direction.DOWN if (speed < 0) else Direction.UP
        if not self.lane.is_forward():
            car_direction = car_direction.opposite
        return car_direction

    def _compute_pos_on_segment(self) -> float:
        segment_start_pos = self.start_segment.get_position(self.ts)[self.road.orientation.value]
        match self.car_direction:
            case Direction.RIGHT:
                return self.pos_on_lane - segment_start_pos
            case Direction.LEFT:
                return self.start_segment.get_size_in_direction(self.ts) - (self.pos_on_lane - segment_start_pos)
            case Direction.UP:
                return self.start_segment.get_size_in_direction(self.ts) - (segment_start_pos - self.pos_on_lane)
            case Direction.DOWN:
                return segment_start_pos - self.pos_on_lane

    @staticmethod
    def validate_environment(ts: TrafficSnapshotReader, pos_on_lane: float, lane: Lane) -> bool:
        # ensure the car is placed on a lane segment (not a crossing)
        return isinstance(ts.get_segment_from_lane_position(lane, pos_on_lane), LaneSegment)

    def build(self) -> CarEnvironment:
        turn_segment: LaneSegment = find_turn_intent_segment(self.ts, self.start_segment, self.specified_turn_intent,
                                                             self.car_direction)

        # We first compute the unbounded path segments (we suppose the car has an infinite horizon).
        # We then compute the horizon and cut off the unbounded path segments.
        unbounded_path_segments: list[Segment] | None = compute_path_through_crossing(self.ts, self.start_segment,
                                                                                      turn_segment)
        if unbounded_path_segments is None:
            raise ValueError("Car specified a turn intent with invalid path.")
        horizon = self._compute_horizon(unbounded_path_segments)
        physical_segment_intervals: list[SegmentInterval] = compute_segment_intervals(
            self.ts,
            unbounded_path_segments,
            self.pos_on_segment,
            self.car_params.get_braking_dist(self.settings.braking_acceleration)
        )
        path_segment_intervals: list[SegmentInterval] = compute_segment_intervals(
            self.ts,
            unbounded_path_segments,
            horizon.start,
            horizon.length(),
        )

        # We update the turn_segment if the next crossing is not in the view of the car.
        # This has the advantage we can safely rely on the turn_segment to compute the multi-view
        # without having to check the visibility of the turn segment again.
        turn_direction = self.specified_turn_direction
        if turn_segment not in unbounded_path_segments:
            end_lane: Segment = unbounded_path_segments[-1]
            if not isinstance(end_lane, LaneSegment):
                raise ValueError("Path must end on a lane segment.")
            turn_segment = end_lane
            turn_direction = TurnDirection.STRAIGHT

        parallel_virtual_lanes, relative_parallel_virtual_lanes = self.compute_parallel_virtual_lanes_intervals(
            unbounded_path_segments,
            horizon,
            turn_segment,
            turn_direction
        )

        reserved_segment_intervals: list[SegmentInterval] = compute_segments_safety_envelope(
            self.ts,
            unbounded_path_segments,
            self.pos_on_segment,
            self.car_params.get_braking_dist(self.settings.braking_acceleration),
            self.car_params.length
        )
        claimed_segment_intervals: list[SegmentInterval] = self._compute_claimed_envelope(
            reserved_segment_intervals,
            self.car_params.transition,
        )

        car_environment = CarEnvironment(
            self.car_direction,
            turn_direction,
            unbounded_path_segments,
            horizon,
            parallel_virtual_lanes,
            relative_parallel_virtual_lanes,
            path_segment_intervals,
            physical_segment_intervals,
            reserved_segment_intervals,
            claimed_segment_intervals
        )
        car_environment.print_debug(self.ts, self.car_params.name)
        return car_environment

    def _compute_horizon(self, unbounded_path_segments: list[Segment]) -> Interval:
        braking_dist: float = self.settings.braking_distance()

        backward_length: float = max(0.0, self.pos_on_segment - braking_dist)
        forward_length: float = 0.0

        remaining_forward_length: float = self.pos_on_segment + braking_dist
        for segment in unbounded_path_segments:
            if remaining_forward_length <= 0:
                break

            if segment.is_lane_segment:
                segment_size = segment.get_size_in_direction(self.ts)
                segment_occupation_size = min(remaining_forward_length, segment_size)
                remaining_forward_length -= segment_occupation_size
                forward_length += segment_occupation_size
            else:
                forward_length += segment.get_size_in_direction(self.ts)

        return Interval(backward_length, forward_length)

    def compute_parallel_virtual_lanes_intervals(
            self,
            unbounded_path: list[Segment],
            horizon: Interval,
            turn_segment: LaneSegment,
            turn_direction: TurnDirection
    ) -> tuple[list[list[VirtualLane]], list[list[VirtualLane]]]:
        # We first compute the (unbounded) parallel virtual lanes segments (each segment is not yet equipped with its
        # interval information).
        parallel_segments = self.compute_parallel_virtual_lanes(unbounded_path, turn_segment, turn_direction)

        parallel_virtual_lanes_intervals: list[list[VirtualLane]] = []
        # Relative in the sense of the segment position.
        # For example ([car_pos_on_seg_1, seg_1_end], [0, seg_2_end], [0, seg_3_end], [0, horizon_end_on_seg_4]).
        parallel_virtual_lanes_relative_intervals: list[list[VirtualLane]] = []

        # Naively, one could just compute the intervals of each parallel-virtual-lane segment inside the horizon of ego.
        # However, on turns at crossings, this would result in ego seeing varying distances *behind* the crossing,
        # since the *length behind the crossing* of the path of ego [lane1, cs, cs, cs, lane2] will be less than
        # in the virtual lane [other_lane, cs, lane2].
        # To solve this problem, we only measure the distance the car travels on lane segments.
        for parallel_segment in parallel_segments:
            virtual_lanes: list[VirtualLane] = []
            relative_virtual_lanes: list[VirtualLane] = []

            for segment_list in parallel_segment:
                virtual_lanes.append(self._segments_to_virtual_lane(segment_list, horizon))
                relative_virtual_lanes.append(
                    VirtualLane(compute_segment_intervals(self.ts, segment_list, horizon.start, horizon.length()))
                )

            parallel_virtual_lanes_intervals.append(virtual_lanes)
            parallel_virtual_lanes_relative_intervals.append(relative_virtual_lanes)

        return parallel_virtual_lanes_intervals, parallel_virtual_lanes_relative_intervals

    def _segments_to_virtual_lane(self, segments: list[Segment], horizon: Interval) -> VirtualLane:
        current_pos = horizon.start
        segment_intervals: list[SegmentInterval] = []

        for i, segment in enumerate(segments):
            # in the first iteration, we need to add the remaining length of the segment to the current position
            segment_size = segment.get_size_in_direction(self.ts)
            segment_length = (segment_size - current_pos) if i == 0 else segment_size

            physical_end = current_pos + segment_length
            view_end = min(physical_end, horizon.end)

            interval = Interval(current_pos, view_end)
            segment_intervals.append(SegmentInterval(segment, interval))

            if view_end < physical_end:
                break

            current_pos += segment_length

        return VirtualLane(segment_intervals)

    def compute_parallel_virtual_lanes(
            self, path: list[Segment],
            turn_segment: LaneSegment,
            turn_direction: TurnDirection
    ) -> list[list[list[Segment]]]:
        through_crossing = any(map(lambda seg: not seg.is_lane_segment, path))
        if through_crossing:
            return self._compute_parallel_virtual_lanes_crossing(turn_segment, turn_direction)
        else:
            # no crossing found
            parallel_lane_segments: list[LaneSegment] = compute_parallel_lane_segments(self.ts, self.start_segment)
            parallel_segments: list[list[Segment]] = []

            for parallel_lane_segment in parallel_lane_segments:
                parallel_segments.append([parallel_lane_segment])

            parallel_segments.sort(key=lambda lane: lane[0].lane.lane_index)

            return [parallel_segments]

    def _compute_parallel_virtual_lanes_crossing(
            self, turn_segment: LaneSegment,
            turn_direction: TurnDirection) -> list[list[list[Segment]]]:
        src_segments: list[LaneSegment] = compute_parallel_lane_segments(self.ts, self.start_segment, 1)
        start_road_orientation: RoadOrientation = self.ts.get_road_by_uid(self.start_segment.lane.road_uid).orientation

        if start_road_orientation == RoadOrientation.VERTICAL and turn_direction == TurnDirection.LEFT:
            src_segments.reverse()

        target_segments: list[LaneSegment] = compute_parallel_lane_segments(self.ts, turn_segment)

        def goes_into_crossing(segment: LaneSegment) -> bool:
            return compute_path_through_crossing(self.ts, self.start_segment, segment) is not None

        order_lanes: list[list[list[Segment]]] = []
        for src_seg in src_segments:
            if goes_into_crossing(src_seg):
                if src_seg == self.start_segment:
                    path: list[Segment] = compute_path_through_crossing(self.ts, self.start_segment, turn_segment)
                    if path is not None:
                        order_lanes.append([path])
                else:
                    paths = []
                    for target_segment in target_segments:
                        if not goes_into_crossing(target_segment):
                            continue
                        path: list[Segment] = compute_path_through_crossing(self.ts, src_seg, target_segment)
                        if path is not None:
                            paths.append(path)
                    order_lanes.append(paths)
            else:
                paths = []
                for target_segment in target_segments:
                    if goes_into_crossing(target_segment):
                        continue
                    path: list[Segment] = compute_path_through_crossing(self.ts, target_segment, src_seg)
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

    def _compute_claimed_envelope(self, reserved_segment_intervals: list[SegmentInterval], transition: float) -> list[
        SegmentInterval]:
        if transition == 0 or len(reserved_segment_intervals) != 1:
            return []

        segment_interval: SegmentInterval = reserved_segment_intervals[0]
        if not isinstance(segment_interval.segment, LaneSegment):
            raise ValueError("Car cannot transition on a non-lane segment.")

        lane_segment: LaneSegment = segment_interval.segment

        parallel_segments = compute_parallel_lane_segments(self.ts, lane_segment)
        current_index = parallel_segments.index(lane_segment)

        road = self.ts.get_road_by_uid(segment_interval.segment.lane.road_uid)
        delta = 1 if transition > 0 else -1
        if road.orientation == RoadOrientation.HORIZONTAL:
            delta = -delta

        # 1 means up/right, -1 means down/left
        # The segments are sorted by lane index which matches this mapping.
        claimed_segment_index = current_index + delta
        claimed_segment = parallel_segments[claimed_segment_index]

        return [SegmentInterval(claimed_segment, segment_interval.interval)]
