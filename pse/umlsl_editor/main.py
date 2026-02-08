"""
Main entry point for the UMLSL Traffic Editor application.
"""
import os
import sys
import warnings

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.view.ui.exeption_handling.exeption_handler import ExceptionHandler
from pse.umlsl_editor.src.view.ui.main_window import MainWindow


class Main:
    """Main Application Controller."""

    def __init__(self):
        self.application_controller = ApplicationController()

        self.open_window()

    def open_window(self) -> None:
        """Launch the main window with a sample scene for testing."""
        app = QApplication(sys.argv)

        app.setApplicationName("UMLSL Traffic Editor")
        app.setApplicationDisplayName("UMLSL Traffic Editor")

        # 3. Set the Icon
        # Ideally, use an absolute path or ensure the file is next to the script
        icon_path = os.path.join(os.path.dirname(__file__), "src", "view", "widgets", "qt_widgets", "icons", "icon.png")
        app.setWindowIcon(QIcon(icon_path))

        window = MainWindow(self.application_controller)

        exception_handler = ExceptionHandler(parent=window)
        # sys.excepthook = exception_handler.handle_exception
        warnings.showwarning = exception_handler.handle_warning

        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    Main()
