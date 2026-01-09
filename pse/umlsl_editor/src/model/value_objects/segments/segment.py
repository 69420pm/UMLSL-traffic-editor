from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class Segment(ABC):
    is_lane_segment: bool


@dataclass
class Path:
    segments: list[Segment]