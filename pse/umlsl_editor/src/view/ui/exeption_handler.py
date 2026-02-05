import sys
import traceback

from PySide6.QtWidgets import QMessageBox


# --- 1. Error Handler (Crashes) ---
def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    box = QMessageBox()
    box.setIcon(QMessageBox.Critical)
    box.setWindowTitle("Critical Error")
    box.setText(f"An unexpected error occurred:\n{exc_value}")
    box.setDetailedText(error_msg)
    box.setStandardButtons(QMessageBox.Ok)
    box.exec()


# --- 2. Warning Handler (Non-fatal) ---
def global_warning_handler(message, category, filename, lineno, file=None, line=None):
    """
    Redirects warnings.warn() to a QMessageBox.
    """
    msg_text = str(message)

    box = QMessageBox()
    box.setIcon(QMessageBox.Warning)  # Use the Yellow Warning Triangle
    box.setWindowTitle("Warning")
    box.setText(f"{category.__name__}:\n{msg_text}")
    # Optional: Add file/line info to details
    box.setDetailedText(f"File: {filename}\nLine: {lineno}")
    box.setStandardButtons(QMessageBox.Ok)
    box.exec()
