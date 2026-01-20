from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.controllers import ApplicationController


class LoadTrafficSnapshot(Command[None]):
    """Loads a traffic_snapshot from a specified file path and updates the application controller's traffic snapshot,
    which in turn basically reloads the program with the new traffic_snapshot."""
    def __init__(self, file_path: str, application_controller: ApplicationController):
        self._file_path = file_path
        self._application_controller = application_controller

    def execute(self) -> None:
        """Loads a traffic_snapshot from the specified file path and
         update the traffic snapshot in the application_controller.

        Raises:
            CommandValidationError: If command validation fails.
        """
        pass