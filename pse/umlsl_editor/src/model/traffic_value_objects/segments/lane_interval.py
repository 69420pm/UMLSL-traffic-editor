from dataclasses import dataclass

from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment


@dataclass(frozen=True, kw_only=True)
class LaneInterval:
    """The lane interval describes an interval on a single lane segment."""
    lane_segment: LaneSegment
    start: float
    end: float
