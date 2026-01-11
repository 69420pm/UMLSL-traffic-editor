from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.view_models.selection import Selection
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_reader import TrafficSnapshotReader


class SelectRoad(Command[None]):
    """Selects a road in the traffic snapshot editor."""

    def __init__(self, road_id: str, selection: Selection, traffic_snapshot_reader: TrafficSnapshotReader):
        """
        Initialize the SelectRoadCommand with the road identifier.

        Args:
            road_id: Unique identifier of the road to be selected.
            selection: Selection manager.
            traffic_snapshot_reader: TrafficSnapshot reader
        """
        self.road_id = road_id
        self._selection = selection
        self._traffic_snapshot_reader = traffic_snapshot_reader

    def execute(self) -> None:
        """
        Selects the specified road in the traffic snapshot editor.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError