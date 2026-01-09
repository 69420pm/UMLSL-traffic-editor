from pse.umlsl_editor.src.commands.command import Command


class ToggleCoordinateSystem(Command[None]):
    """
    Toggles weather the coordinate system in the visual editor should be rendered.
    """

    def execute(self) -> None:
        """
        Toggles the visualization of the coordinate system.
        """
        raise NotImplementedError