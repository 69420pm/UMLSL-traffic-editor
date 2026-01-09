from pse.umlsl_editor.src.commands.command import Command


class ToggleSafetyDistanceCommand(Command[None]):
    """
    Toggles weather the safety distance of the cars in the visual editor should be rendered.
    """

    def execute(self) -> None:
        """
        Toggles the visualization of the safety distance.
        """
        raise NotImplementedError