import json
import os

from pse.umlsl_editor.src.commands.command import Command, CommandValidationError
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import (
    TrafficSnapshotModel,
)
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import (
    TrafficSnapshotReader,
)
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import (
    UMLSLQueriesModel,
)
from pse.umlsl_editor.src.services.external_persistence_service import (
    ExternalPersistenceService,
)
from pse.umlsl_editor.src.services.persistence_service import PersistenceService


class ExportSnapshot(Command[None]):
    """Saves the current traffic snapshot to a specified file path."""

    def __init__(self, file_path: str, traffic_snapshot_model: TrafficSnapshotModel, umlsl_queries: UMLSLQueriesModel):
        """
        Initialize the SaveAsTrafficSnapshot command with the target file path.

        Args:
            file_path: The path where the traffic snapshot will be saved.
            traffic_snapshot_reader: The traffic snapshot reader for the current application.
            umlsl_queries: The UMLSL queries interface for accessing UMLSL-related data.
        """
        self._file_path = file_path
        self._traffic_snapshot_model = traffic_snapshot_model

    def execute(self) -> None:
        """
        Saves the current traffic snapshot to the specified file path.

        Raises:
            CommandValidationError: If command validation fails.
        """
        if not self._file_path:
            raise CommandValidationError("File path is required to save a snapshot.")

        try:
            filename_without_ext = os.path.splitext(os.path.basename(self._file_path))[0]
            payload = ExternalPersistenceService.serialize(
                snapshot=self._traffic_snapshot_model,
                filename=filename_without_ext
            )
        except ValueError as exc:
            raise CommandValidationError(f"Failed to serialize snapshot: {exc}") from exc

        try:
            with open(self._file_path, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2)
        except OSError as exc:
            raise CommandValidationError(f"Failed to save snapshot: {exc}") from exc
