from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval


def compute_segment_intervals(
        ts: TrafficSnapshotReader,
        path: list[Segment],
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

        if i >= len(path):
            return result

        seg_i = path[i]

        b_i: float
        if seg_i.is_lane_segment:
            b_i = min(interval_start_offset + current_size, seg_i.get_size_in_direction(ts))
        else:
            b_i = seg_i.get_size_in_direction(ts)

        interval = Interval(interval_start_offset, b_i)
        next_size = current_size - interval.length()

        interval_start_offset = 0

        result.append(SegmentInterval(seg_i, interval))
        i += 1

    return result


def compute_segments_safety_envelope(
        ts: TrafficSnapshotReader,
        path: list[Segment],
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
    size = horizon_size

    i = 0
    while size > 0 and i < len(path):
        seg_i = path[i]
        seg_size = seg_i.get_size_in_direction(ts)

        b_i: float
        if seg_i.is_lane_segment:
            b_i = min(interval_start_offset + size, seg_size)
            length = b_i - interval_start_offset
            size -= length
        else:
            b_i = seg_size
            length = b_i - interval_start_offset
            # if the car ends in a crossing, we make sure the segment_intervals are expanded until after the crossing
            size = max(size - length, car_size)

        interval = Interval(interval_start_offset, b_i)

        interval_start_offset = 0

        result.append(SegmentInterval(seg_i, interval))
        i += 1

    return result
