from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.domain_models.settings import Settings


class ToggleCoordinateSystem(Command[None]):
    """
    Toggles between different coordinate systems in the UMLSL editor.
    """

    def __init__(self, settings: Settings):
        """
        Initialize the ToggleCoordinateSystem command with the settings.

        Args:
            settings: Settings object.
        """
        self._settings = settings

    def execute(self) -> None:
        """
        Toggles the coordinate system used in the UMLSL editor.
        """
        raise NotImplementedError