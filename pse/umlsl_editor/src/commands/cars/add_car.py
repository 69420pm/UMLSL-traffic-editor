from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.entities.car import CarParams, Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_writer import TrafficSnapshotWriter


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
        self._traffic_snapshot_writer = traffic_snapshot_writer
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self.car_params = car_params

    def execute(self) -> None:
        """
        Creates a Car instance using the provided parameters, validates it through
        Car.__post_init__, and adds it to the traffic snapshot.
        
        Raises:
            CommandValidationError: If command validation fails.
        """
        car = Car(self._traffic_snapshot_reader, self._traffic_snapshot_writer, self.car_params)
        # TODO: Convert car_params to actual car arguments and get segments, only for demonstration now
        self._traffic_snapshot_writer.add_car(car)
        # TODO: Error Handling
        raise NotImplementedError("Prototype Method")

