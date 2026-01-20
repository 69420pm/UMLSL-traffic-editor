from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.settings import Settings


class ToggleSafetyDistanceCommand(Command[None]):
    """
    Toggles weather the safety distance of the cars in the visual editor should be rendered.
    """
    def __init__(self, settings: Settings):
        """
        Initialize the ToggleSafetyDistanceCommand with the settings.

        Args:
            settings: Settings object.
        """
        self._settings = settings

    def execute(self) -> None:
        """
        Toggles the visualization of the safety distance.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError