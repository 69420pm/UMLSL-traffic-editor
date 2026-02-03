import sys
import warnings

from PySide6.QtWidgets import QApplication

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.exeption_handler import global_exception_handler, global_warning_handler
from pse.umlsl_editor.src.view.ui.main_window import MainWindow


class Main:
    """Main Application Controller."""

    def __init__(self):
        self.application_controller = ApplicationController()

        self.open_window()

    def open_window(self) -> None:
        """Launch the main window with a sample scene for testing."""
        app = QApplication(sys.argv)

        sys.excepthook = global_exception_handler
        warnings.showwarning = global_warning_handler

        window = MainWindow(self.application_controller)

        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    Main()
