from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel


class ToggleCoordinateSystemCommand(Command[None]):
    """
    Toggles between different coordinate systems in the UMLSL editor.
    """

    def __init__(self, settings: SettingsModel):
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
        self._settings.set_render_coordinate_system()
        raise NotImplementedError("Prototype Method")
