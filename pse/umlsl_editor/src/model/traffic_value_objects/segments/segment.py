from abc import ABC, abstractmethod
from dataclasses import dataclass

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader


@dataclass(frozen=True)
class Segment(ABC):
    is_lane_segment: bool
    uid: str

    @abstractmethod
    def get_position(self, traffic_snapshot_reader: TrafficSnapshotReader) -> tuple[float, float]:
        """Return position of the top left corner of the path.
        It gets calculated from the position of the first segment."""
        pass

    @abstractmethod
    def get_size(self, traffic_snapshot_reader: TrafficSnapshotReader) -> tuple[float, float]:
        """Return size (width, height) of the path."""
        pass


@dataclass
class Path:
    """Describes a list of ordered segments"""
    segments: list[Segment]

    def __post_init__(self) -> None:
        self.validate()
        self._initialized = True

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

