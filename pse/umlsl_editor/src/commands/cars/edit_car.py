from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.entities.car import CarParams, Car


class EditCarCommand(Command[None]):
    """Edits the properties of an existing car in the traffic snapshot."""

    def __init__(
        self,
        traffic_snapshot_reader,
        traffic_snapshot_writer,
        car_params: CarParams
    ):
        """
        Initialize the EditCarCommand with the car's unique identifier and updated parameters.

        Args:
            traffic_snapshot_reader: Interface to read from the traffic snapshot.
            traffic_snapshot_writer: Interface to write to the traffic snapshot.
            car_params: Parameters to change
        """
        self._traffic_snapshot_writer = traffic_snapshot_writer
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self.car_params = car_params


    def execute(self) -> None:
        """
        Edits the properties of the car with the specified unique identifier in the traffic snapshot.

        Raises:
            CommandValidationError: If command validation fails.
        """
        car = self._traffic_snapshot_reader.get_car_by_name(self.car_params.name)
        self._traffic_snapshot_writer.update_car(car, self.car_params)
        raise NotImplementedError("Prototype Method")