from pse.umlsl_editor.src.commands.command import Command, ReturnValue
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter


class ChangeBreakingAcceleration(Command[None]):
    """
    Changes the breaking acceleration of the cars based on the provided parameters.
    """

    def __init__(
            self,
            settings: SettingsModel,
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