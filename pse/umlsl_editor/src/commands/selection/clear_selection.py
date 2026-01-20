from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.view_models.selection import Selection


class ClearSelection(Command[None]):
    """Clears the current selection in the traffic snapshot editor."""

    def __init__(self, selection: Selection):
        """
        Initialize the ClearSelectionCommand with the selection manager.

        Args:
            selection: Selection manager.
        """
        self._selection = selection

    def execute(self) -> None:
        """
        Clears the current selection in the traffic snapshot editor.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError