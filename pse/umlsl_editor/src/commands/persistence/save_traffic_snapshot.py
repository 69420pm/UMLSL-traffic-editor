from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.view_models.umlsl_queries import UMLSLQueries


class SaveTrafficSnapshot(Command[None]):
    """Saves the current traffic snapshot to its associated file path, where a traffic_snapshot is already stored."""

    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader, umlsl_queries: UMLSLQueries):
        """
        Initialize the SaveTrafficSnapshot command.

        Args:
            traffic_snapshot_reader: The traffic snapshot reader for the current application.
            umlsl_queries: The UMLSL queries interface for accessing UMLSL-related data.
        """
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self._umlsl_queries = umlsl_queries

    def execute(self) -> None:
        """
        Saves the current traffic snapshot to its associated file path.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError