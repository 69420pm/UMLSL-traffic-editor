from pse.umlsl_editor.src.commands.command import Command


class DeleteCar(Command[None]):
    """Deletes a car from the traffic snapshot based on its unique identifier."""


    def __init__(
        self,
        traffic_snapshot_writer,
        traffic_snapshot_reader,
        car_id: str
    ):
        """
        Initialize the DeleteCarCommand with the car's unique identifier.

        Args:
            traffic_snapshot_writer: Interface to write to the traffic snapshot.
            traffic_snapshot_reader: Interface to read from the traffic snapshot.
            car_id: Unique identifier of the car to be deleted.
        """
        self._traffic_snapshot_writer = traffic_snapshot_writer
        self._traffic_snapshot_reader = traffic_snapshot_reader
        self.car_id = car_id

    def execute(self) -> None:
        """
        Deletes the car with the specified unique identifier from the traffic snapshot.

        Raises:
            CommandValidationError: If command validation fails.
        """
        #TODO: Error Handling
        self._traffic_snapshot_writer.remove_car(self.car_id)
        raise NotImplementedError("Prototype Method")