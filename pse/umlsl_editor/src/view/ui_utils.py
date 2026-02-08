"""
UI utility functions for the UMLSL Traffic Editor.

Provides helper functions for loading Qt Designer UI files.
"""
from typing import Optional

from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget


def load_ui(path: str, parent: Optional[QWidget] = None) -> Optional[QWidget]:
    """
    Load a Qt Designer UI file and return the corresponding widget.

    Args:
        path: Path to the .ui file to load.
        parent: Optional parent widget for the loaded UI.

    Returns:
        The loaded QWidget, or None if loading failed.
    """
    loader = QUiLoader()
    file = QFile(path)

    if not file.open(QFile.ReadOnly):
        print(f"CRITICAL ERROR: Could not open {path}")
        return None

    widget = loader.load(file, parent)
    file.close()
    return widget
