from pse.umlsl_editor.src.commands.command import Command, ReturnValue
from pse.umlsl_editor.src.controllers import ApplicationController


class LoadTrafficSnapshot(Command[None]):
    def __init__(self, file_path: str, application_controller: ApplicationController):
        self._file_path = file_path

    def execute(self) -> None:
        """Loads a traffic_snapshot from the specified file path and
         update the traffic snapshot in the application_controller."""
        pass