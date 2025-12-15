from pse.umlsl_editor.traffic_snapshot import TrafficSnapshot


class PersistenceService:
    """Handles saving/loading JSON (MC10)."""

    def serialize(self, snapshot: TrafficSnapshot) -> str:
        pass

    def deserialize(self, json_data: str) -> TrafficSnapshot:
        # Includes error correction (MC11)
        pass