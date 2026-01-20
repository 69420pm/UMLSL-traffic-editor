from pse.umlsl_editor.src.commands.command import Command, ReturnValue
from pse.umlsl_editor.src.model.view_models.settings import Settings
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.view_models.traffic_snapshot_writer import TrafficSnapshotWriter


class ChangeBreakingAcceleration(Command[None]):
    """
    Changes the breaking acceleration of the cars based on the provided parameters.
    """

    def __init__(
            self,
            settings: Settings,
            value: int
    ):
        """
        Initialize the AddCarCommand with car parameters.

        Args:
            settings: Settings object.
            value: Breaking acceleration value .
        """
        self.value = value
        self._settings = settings

    def execute(self) -> ReturnValue:
        """
        Changes the breaking acceleration.
        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError