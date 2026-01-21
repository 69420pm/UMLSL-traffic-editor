from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.selection import Selection
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader


class DeselectRoad(Command[None]):
    """Deselects a road in the traffic snapshot editor."""

    def __init__(self, road_id: str, selection: Selection, traffic_snapshot_reader: TrafficSnapshotReader):
        """
        Initialize the DeselectRoadCommand with the road identifier and selection manager.

        Args:
            road_id: Unique identifier of the road to be deselected.
            selection: Selection manager.
        """
        self.road_id = road_id
        self._selection = selection
        self._traffic_snapshot_reader = traffic_snapshot_reader

    def execute(self) -> None:
        """
        Deselects the specified road in the traffic snapshot editor.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError