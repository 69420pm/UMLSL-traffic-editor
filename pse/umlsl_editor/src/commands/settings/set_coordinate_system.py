from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel


class SetCoordinateSystemCommand(Command[None]):
    """
    Toggles between different coordinate systems in the UMLSL editor.
    """

    def __init__(self, settings: SettingsModel, value: bool):
        """
        Initialize the ToggleCoordinateSystem command with the settings.

        Args:
            settings: Settings object.
        """
        self._settings = settings
        self.value = value

    def execute(self) -> None:
        """
        Toggles the coordinate system used in the UMLSL editor.
        """
        self._settings.set_render_coordinate_system(self.value)
