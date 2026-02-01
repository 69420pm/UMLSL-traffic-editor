from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter


class SelectEntity(Command[None]):
    """Deselects a car from the current selection in the traffic snapshot editor."""

    def __init__(
            self,
            traffic_snapshot_writer: TrafficSnapshotWriter,
            uid: str
    ):
        """
        Initialize the DeselectCarCommand with the selection manager and car ID.

        Args:
            uid: Unique identifier of the car to be deselected.
        """
        self._traffic_snapshot_writer = traffic_snapshot_writer
        self.uid = uid

    def execute(self) -> None:
        print(self.uid)
        self._traffic_snapshot_writer.select_entity(self.uid)
