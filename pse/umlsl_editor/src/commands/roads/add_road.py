from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.entities.road import RoadParams, Road


class AddRoad(Command[None]):
    """Adds a new road to the traffic snapshot."""

    def __init__(
            self,
            traffic_snapshot_writer: TrafficSnapshotWriter,
            traffic_snapshot_reader: TrafficSnapshotReader,
            road_params: RoadParams
    ):
        """
        Initialize the AddRoadCommand with the road parameters.

        Args:
            traffic_snapshot_writer: Interface to write to the traffic snapshot.
            traffic_snapshot_reader: Interface to read from the traffic snapshot.
            road_params: Parameters of the road to be added.
        """
        self._traffic_snapshot_writer = traffic_snapshot_writer
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self.road_params = road_params

    def execute(self) -> None:
        """
        Adds a new road to the traffic snapshot.

        Raises:
            CommandValidationError: If command validation fails.
        """
        self._traffic_snapshot_reader.validate_road_params(self.road_params, True)
        road = Road.from_params(self.road_params)
        self._traffic_snapshot_writer.add_road(road)
        # TODO: Error Handling
        raise NotImplementedError("Prototype Method")
