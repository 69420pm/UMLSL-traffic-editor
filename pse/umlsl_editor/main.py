import sys

from PySide6.QtWidgets import QApplication

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.view.ui.main_window import MainWindow
from pse.umlsl_editor.src.view.view_event_handler_impl import ViewEventHandlerImplementation


class Main:
    """Main Application Controller."""

    def __init__(self):
        self.application_controller = ApplicationController( )
        self.open_windwo()

    def open_windwo(self) -> None:
        """Launch the main window with a sample scene for testing."""
        app = QApplication(sys.argv)
        window = MainWindow(self.application_controller)
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    Main()