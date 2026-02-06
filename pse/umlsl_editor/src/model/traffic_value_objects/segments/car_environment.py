from enum import Enum

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.position import Position
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import VirtualLane, Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection
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
            pos_on_lane: float,
            car_size: float,
            speed: float,
            turn_direction: TurnDirection
    ) -> 'CarEnvironment':
        road_id = car_lane.road_uid
        road = ts.get_road_by_uid(road_id)
        segment = ts.get_segment_from_lane_position(car_lane, pos_on_lane)

        # todo: extract into separate method
        if road.orientation == RoadOrientation.HORIZONTAL:
            car_direction = Direction.LEFT if speed < 0 else Direction.RIGHT
        else:
            car_direction = Direction.UP if speed < 0 else Direction.DOWN

        print("car lane ", car_lane, " pos on lane: ", pos_on_lane, " segment ", segment, " car dir ", car_direction)
        lane_pos = car_lane.get_one_dimensional_position(ts)
        print("lane pos is ", lane_pos, " pos on lane: ", pos_on_lane, " direction is ", car_direction)

        if turn_direction == TurnDirection.STRAIGHT:
            # path = _compute_path_straight(ts, car_direction, segment)
            # print("path is ", path)
            return CarEnvironment()
        else:
            # todo
            return CarEnvironment()
        #  visible_segments = _compute_visible_segments(traffic_snapshot, path, pos, car_size)

        #  interval_start_offset = pos.clone().lane_pos


def _compute_path_straight(ts: TrafficSnapshotReader, car_direction: Direction, segment: Segment) -> VirtualLane:
    path = [segment]
    next_segment = ts.get_adjacent_segment(segment.uid, car_direction)
    while next_segment is not None:
        path.append(next_segment)
        next_segment = ts.get_adjacent_segment(next_segment.uid, car_direction)

    return VirtualLane(path)


def _compute_path() -> VirtualLane:
    pass


def _compute_visible_segments(ts: TrafficSnapshotReader, path: VirtualLane, pos: Position, car_lane: LaneSegment,
                              car_size: float) -> list[SegmentInterval]:
    start_pos = car_lane.lane.get_one_dimensional_position(ts)

    return []


def _compute_visible_segments_iteratively(ts: TrafficSnapshotReader, path: VirtualLane, seg_orientations: list[Orientation],
                                          interval_start_offset: float, pos: Position, car_size: float) -> list[
    SegmentInterval]:
    # todo: take pos component into account
    result = []

    next_size = car_size

    i = 0
    while True:
        current_size = next_size
        seg_i = path.segments[i]
        orientation = seg_orientations[i]

        b_i: float
        if seg_i.is_lane_segment:
            b_i = min(interval_start_offset + current_size, seg_i.get_size(ts)[orientation.value])
        else:
            b_i = seg_i.get_size(ts)[orientation.value]

        interval = Interval(interval_start_offset, b_i)
        next_size = current_size - interval.length()

        if next_size > 0:
            interval_start_offset = 0
        else:
            result.append(SegmentInterval(seg_i, interval, 0))  # todo: virtual pos

        if next_size <= 0:
            return result
        else:
            i += 1
