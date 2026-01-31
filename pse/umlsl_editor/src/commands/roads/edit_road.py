from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.entities.road import RoadParams


class EditRoad(Command[None]):
    """Edits the properties of an existing road in the traffic snapshot."""

    def __init__(
            self,
            traffic_snapshot_reader: TrafficSnapshotReader,
            traffic_snapshot_writer: TrafficSnapshotWriter,
            road_params: RoadParams,
            uid: str
    ):
        """
        Initialize the EditRoadCommand with the road's unique identifier and updated parameters.

        Args:
            traffic_snapshot_reader: Interface to read from the traffic snapshot.
            traffic_snapshot_writer: Interface to write to the traffic snapshot.
            road_params: Parameters to change
            uid: Unique identifier of the road to edit.
        """
        self._traffic_snapshot_writer = traffic_snapshot_writer
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self.road_params = road_params
        self.uid = uid

    def execute(self) -> None:
        """
        Edits the properties of the road with the specified unique identifier in the traffic snapshot.

        Raises:
            CommandValidationError: If command validation fails.
        """
        self._traffic_snapshot_reader.validate_road_params(self.road_params, False)
        self._traffic_snapshot_writer.update_road(uid, self.road_params)
        raise NotImplementedError("Prototype Method")
