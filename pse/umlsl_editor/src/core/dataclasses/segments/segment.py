from abc import ABC
from dataclasses import dataclass


@dataclass
class Segment(ABC):
    is_lane_segment: bool


@dataclass
class Path:
    segments: list[Segment]