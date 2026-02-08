from dataclasses import dataclass

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


@dataclass
class SegmentInterval:
    """
    Represents a segment interval on the virtual lane of the car.
    """
    segment: Segment
    interval: Interval

    def get_global_interval(self, ts: TrafficSnapshotReader):
        """
        The interval stored as a property in this class is purely relative to the segment and the car's driving direction.
        This function converts the interval to a global interval. That means adding the target coordinate of the
        segment's start position to the interval yields the interval with global coordinates. (Target means for horizontal
        lanes it is the x position, for vertical lanes it is the y position.)
        """

        # todo
        return self.interval

    def __str__(self):
        return f"{self.segment} {self.interval}"