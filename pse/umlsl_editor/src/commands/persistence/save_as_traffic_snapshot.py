from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel


class SaveAsTrafficSnapshot(Command[None]):
    """Saves the current traffic snapshot to a specified file path."""

    def __init__(self, file_path: str, traffic_snapshot_reader:TrafficSnapshotReader, umlsl_queries: UMLSLQueriesModel):
        """
        Initialize the SaveAsTrafficSnapshot command with the target file path.

        Args:
            file_path: The path where the traffic snapshot will be saved.
            traffic_snapshot_reader: The traffic snapshot reader for the current application.
            umlsl_queries: The UMLSL queries interface for accessing UMLSL-related data.
        """
        self._file_path = file_path
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self._umlsl_queries = umlsl_queries

    def execute(self) -> None:
        """
        Saves the current traffic snapshot to the specified file path.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError