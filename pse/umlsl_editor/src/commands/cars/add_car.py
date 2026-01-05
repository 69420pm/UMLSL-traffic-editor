from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.core.dataclasses.car import CarParams
from pse.umlsl_editor.src.core.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.core.traffic_snapshot_writer import TrafficSnapshotWriter


class AddCarCommand(Command[None]):
    """Creates a car object based on the provided parameters and adds it to the traffic snapshot."""


    def __init__(
        self,
        traffic_snapshot_reader: TrafficSnapshotReader,
        traffic_snapshot_writer: TrafficSnapshotWriter,
        car_params: CarParams
    ):
        """
        Initialize the AddCarCommand with car parameters.

        Args:
            traffic_snapshot_reader: Interface to read from the traffic snapshot.
            traffic_snapshot_writer: Interface to write to the traffic snapshot.
            car_params: Car creation parameters (name, assigned_road, lane_index, etc.).
        """
        self.traffic_snapshot_writer = traffic_snapshot_writer
        self.traffic_snapshot_reader = traffic_snapshot_reader
        self.car_params = car_params

    def execute(self) -> None:
        """
        Creates a Car instance using the provided parameters, validates it through
        Car.__post_init__, and adds it to the traffic snapshot.
        """
        raise NotImplementedError

