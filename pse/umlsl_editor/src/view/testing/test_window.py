# pse/umlsl_editor/src/view/ui/test_window.py
import sys
from PySide6.QtWidgets import QApplication

from pse.umlsl_editor.src.view.ui.main_window import MainWindow

def run_test_render():
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_test_render()