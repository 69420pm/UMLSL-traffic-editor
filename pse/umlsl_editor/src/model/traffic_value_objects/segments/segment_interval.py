from dataclasses import dataclass

from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


@dataclass
class SegmentInterval:
    """ Represents an interval on a segment. The interval completely captures crossing segments. """
    segment: Segment
    interval: Interval