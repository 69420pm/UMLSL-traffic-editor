from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.entities.car import CarParams
from pse.umlsl_editor.src.model.errors.car_errors import CarValidationError


class EditCarCommand(Command[None]):
    """Edits the properties of an existing car in the traffic snapshot."""

    def __init__(
            self,
            traffic_snapshot_reader,
            traffic_snapshot_writer,
            car_params: CarParams,
            uid: str
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
        self.car_uid = uid

    def execute(self) -> None:
        """
        Edits the properties of the car with the specified unique identifier in the traffic snapshot.

        Raises:
            CommandValidationError: If command validation fails.
        """
        if not self._traffic_snapshot_reader.is_car_existing(self.car_uid):
            raise CarValidationError(content=f"Car with UID {self.car_uid} does not exist and cannot be edited.")
        self._traffic_snapshot_reader.validate_car_params(self.car_params, False)
        self._traffic_snapshot_writer.update_car_with_params(self.car_uid, self.car_params)
