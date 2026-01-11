from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class Segment(ABC):
    is_lane_segment: bool
    length: float


@dataclass
class Path:
    segments: list[Segment]