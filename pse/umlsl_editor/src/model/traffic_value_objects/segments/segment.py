from abc import ABC
from dataclasses import dataclass


@dataclass(frozen=True)
class Segment(ABC):
    is_lane_segment: bool
    length: float


@dataclass
class Path:
    segments: tuple[Segment, ...]

    def __post_init__(self) -> None:
        self.validate()
        self._initialized = True

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        if getattr(self, "_initialized", False):
            self.validate()

    def validate(self) -> None:
        if not isinstance(self.segments, tuple):
            raise ValueError("segments must be a tuple")
        for s in self.segments:
            if not isinstance(s, Segment):
                raise ValueError("All elements in segments must be Segment instances")
