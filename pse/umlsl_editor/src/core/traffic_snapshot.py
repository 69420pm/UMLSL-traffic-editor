from typing import Optional

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road
from pse.umlsl_editor.src.core.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.core.traffic_snapshot_writer import TrafficSnapshotWriter


class TrafficSnapshot(TrafficSnapshotReader, TrafficSnapshotWriter):
    """
    Represents the complete state of a traffic simulation.

    Serves as the single source of truth for all roads and cars. Implements both
    TrafficSnapshotReader and TrafficSnapshotWriter interfaces for read/write access.
    """

    def __init__(
        self,
        roads: Optional[dict[str, Road]] = None,
        cars: Optional[dict[str, Car]] = None,
    ):
        self._roads = dict(roads) if roads is not None else {}
        self._cars = dict(cars) if cars is not None else {}
