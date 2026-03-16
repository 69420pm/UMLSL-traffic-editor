from dataclasses import dataclass

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval


@dataclass
class VirtualLane:
    """Describes a list of ordered segments"""
    segments: list[Segment]

    def __post_init__(self) -> None:
        self.validate()
        self._initialized = True

    def segments_in_horizon(self, horizon: Interval, traffic_snapshot: TrafficSnapshotReader) -> list[Segment]:
        segments_in_horizon = []
        next_start = 0

        for segment in self.segments:
            end = next_start + segment.get_size_in_direction(traffic_snapshot)
            virtual_interval = Interval(next_start, end)

            if horizon.intersects(virtual_interval):
                segments_in_horizon.append(segment)

            next_start = end

        return segments_in_horizon

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        if getattr(self, "_initialized", False):
            self.validate()

    def validate(self) -> None:
        if not isinstance(self.segments, list):
            raise ValueError("segments must be a list")
        for s in self.segments:
            if not isinstance(s, Segment):
                raise ValueError("All elements in segments must be Segment instances")


@dataclass
class CarInterval:
    car: 'Car'
    interval: Interval

@dataclass(frozen=True)
class VirtualLaneNew:
    """Describes a list of ordered segments"""
    segment_intervals: list[SegmentInterval]
    car_info: list[CarInterval]

    def segments_in_horizon(self, horizon: Interval) -> list[SegmentInterval]:
        segments_in_horizon = []

        for segment_interval in self.segment_intervals:
            if horizon.intersects(segment_interval.interval):
                segments_in_horizon.append(segment_interval)

        return segments_in_horizon