from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter


class ClearSelection(Command[None]):
    """Clears the current selection in the traffic snapshot editor."""

    def __init__(self, traffic_snapshot_writer: TrafficSnapshotWriter) -> None:
        """
        Initialize the ClearSelectionCommand with the selection manager.

        Args:
            traffic_snapshot_writer: Interface to write to the traffic snapshot.
        """
        self._traffic_snapshot_writer = traffic_snapshot_writer

    def execute(self) -> None:
        """
        Clears the current selection in the traffic snapshot editor.
        """
        self._traffic_snapshot_writer.clear_selection()
