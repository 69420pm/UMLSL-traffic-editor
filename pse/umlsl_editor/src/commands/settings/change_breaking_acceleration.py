from pse.umlsl_editor.src.commands.command import Command, ReturnValue
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.errors.settings_errors import SettingsValidationError


class ChangeBrakingAccelerationCommand(Command[None]):
    """
    Changes the breaking acceleration of the cars based on the provided parameters.
    """

    def __init__(
            self,
            settings: SettingsModel,
            value: float
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
        if self.value <= 0:
            raise SettingsValidationError("Braking acceleration must be a positive value.")
        self._settings.set_braking_acceleration(self.value)
