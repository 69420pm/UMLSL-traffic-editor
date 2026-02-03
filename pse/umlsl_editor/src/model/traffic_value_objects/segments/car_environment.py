from dataclasses import dataclass
from enum import Enum

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.position import Position
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Path
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent

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
    def create_environment(
            traffic_snapshot: TrafficSnapshotReader,
            car_lane: LaneSegment,
            pos: Position,
            car_size: float,
            turn_intent: TurnIntent
    ) -> 'CarEnvironment':
        road_id = car_lane.lane.road_uid
        road = traffic_snapshot.get_road_by_uid(road_id)
        path = _compute_path()
        visible_segments = _compute_visible_segments(traffic_snapshot, path, pos, car_size)


        interval_start_offset = pos.clone().x


        # todo
        pass


def _compute_path() -> Path:
    pass


def _compute_visible_segments(ts: TrafficSnapshotReader, path: Path, pos: Position, car_lane: LaneSegment, car_size: float) -> list[SegmentInterval]:
    start_pos = car_lane.lane.get_one_dimensional_position(ts)


def _compute_visible_segments_iteratively(ts: TrafficSnapshotReader, path: Path, seg_orientations: list[Orientation],
                              interval_start_offset: float, pos: Position, car_size: float) -> list[SegmentInterval]:
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
