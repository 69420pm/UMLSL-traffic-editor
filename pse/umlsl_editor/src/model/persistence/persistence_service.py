from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel


class PersistenceService:
    """Handles saving/loading JSON (MC10)."""

    def serialize(self, snapshot: TrafficSnapshotModel) -> str:
        raise NotImplementedError

    def deserialize(self, json_data: str) -> TrafficSnapshotModel:
        # Includes error correction (MC11)
        raise NotImplementedError
