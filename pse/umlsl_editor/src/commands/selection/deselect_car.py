from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.selection import Selection
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader


class DeselectCar(Command[None]):
    """Deselects a car from the current selection in the traffic snapshot editor."""

    def __init__(
        self,
        selection: Selection,
        traffic_snapshot_reader: TrafficSnapshotReader,
        car_id: str
    ):
        """
        Initialize the DeselectCarCommand with the selection manager and car ID.

        Args:
            selection: Selection manager.
            car_id: Unique identifier of the car to be deselected.
        """
        self._selection = selection
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self.car_id = car_id

    def execute(self) -> None:
        """
        Deselects the car with the specified unique identifier from the current selection.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError