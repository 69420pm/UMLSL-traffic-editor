from dataclasses import dataclass
from enum import Enum

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.position import Position
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Path, Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent, TurnDirection


class Orientation(Enum):
    HORIZONTAL = 0
    VERTICAL = 1


@dataclass
class CarEnvironment:
    """
    This class includes information on how the car interacts with the segments of the traffic snapshot.
    """

    # The list of virtual lanes of the car.
    virtual_lanes: list[Path]
    # The virtual lane that corresponds to the pursuit path of the car.
    path_pursuit: Path
    # The path of the car where each segment is equipped with an interval.
    # Computes by the seg_V method in the paper.
    path_segment_intervals: list[SegmentInterval]

    @staticmethod
    def empty():
        return CarEnvironment([], Path([]), [])

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

        print("car lane ", car_lane, " pos on lane: ", pos_on_lane, " segment " , segment, " car dir ", car_direction)
        lane_pos = car_lane.get_one_dimensional_position(ts)
        print("lane pos is ", lane_pos, " pos on lane: ", pos_on_lane, " direction is ", car_direction)

        if turn_direction == TurnDirection.STRAIGHT:
            path = _compute_path_straight(ts, car_direction, segment)
            print("path is ", path)
            return CarEnvironment([], path, [])
        else:
            # todo
            return CarEnvironment([], Path([]), [])
        #  visible_segments = _compute_visible_segments(traffic_snapshot, path, pos, car_size)

        #  interval_start_offset = pos.clone().lane_pos

def _compute_path_straight(ts: TrafficSnapshotReader, car_direction: Direction, segment: Segment) -> Path:
    path = [segment]
    next_segment = ts.get_adjacent_segment(segment.uid, car_direction)
    while next_segment is not None:
        path.append(next_segment)
        next_segment = ts.get_adjacent_segment(next_segment.uid, car_direction)

    return Path(path)


def _compute_path() -> Path:
    pass


def _compute_visible_segments(ts: TrafficSnapshotReader, path: Path, pos: Position, car_lane: LaneSegment,
                              car_size: float) -> list[SegmentInterval]:
    start_pos = car_lane.lane.get_one_dimensional_position(ts)

    return []


def _compute_visible_segments_iteratively(ts: TrafficSnapshotReader, path: Path, seg_orientations: list[Orientation],
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
            result.append(SegmentInterval(seg_i, interval))

        if next_size <= 0:
            return result
        else:
            i += 1
