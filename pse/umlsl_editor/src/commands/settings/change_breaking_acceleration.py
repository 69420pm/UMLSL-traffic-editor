from pse.umlsl_editor.src.commands.command import Command, ReturnValue
from pse.umlsl_editor.src.model.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.traffic_snapshot_writer import TrafficSnapshotWriter


class ChangeBreakingAcceleration(Command[None]):
    """
    Changes the breaking acceleration of the cars based on the provided parameters.
    """

    def __init__(
            self,
            traffic_snapshot_reader: TrafficSnapshotReader,
            traffic_snapshot_writer: TrafficSnapshotWriter,
            value: int
    ):
        """
        Initialize the AddCarCommand with car parameters.

        Args:
            traffic_snapshot_reader: Interface to read from the traffic snapshot.
            traffic_snapshot_writer: Interface to write to the traffic snapshot.
            value: Breaking acceleration value .
        """
        self.traffic_snapshot_reader = traffic_snapshot_reader
        self.traffic_snapshot_writer = traffic_snapshot_writer
        self.value = value

    def execute(self) -> ReturnValue:
        """
        Changes the breaking acceleration.
        """
        raise NotImplementedError