"""
Test window launcher for the UMLSL Traffic Editor.

Provides a quick way to launch the editor for testing and development.
"""
import sys

from PySide6.QtWidgets import QApplication

from pse.umlsl_editor.src.view.testing.test_scene_generator import TestDataController, TestApplicationController
from pse.umlsl_editor.src.view.ui.main_window import MainWindow


def run_test_render() -> None:
    """Launch the main window with a sample scene for testing."""
    app = QApplication(sys.argv)
    test_application_controller = TestApplicationController()
    window = MainWindow(test_application_controller)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_test_render()