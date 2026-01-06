"""
Runtime .ui loader protocol and placeholder implementation.

This module defines a protocol (`UiLoader`) for loading Qt Designer .ui files at
runtime and a placeholder implementation (`QtDesignerUiLoader`) that can be
wired into the application once the .ui files are ready.

Structure-only:
- No I/O is performed.
- Methods are declared but not implemented.
- Intended to be used together with binder classes to map objectNames to attributes.

Recommended usage pattern (once implemented):
1) Create .ui files in pse/umlsl_editor/resources/ui/
2) Use a UiLoader to load the .ui file into a QWidget/QMainWindow/QDialog.
3) Pass the loaded root to a binder (e.g., MainWindowUiBinder) that finds children.
4) Connect signals and wire logic in controllers, not inside the binder.

Promoted widgets:
- If you use custom widgets (e.g., TrafficCanvasView), configure the loader to
  recognize them (register or override factory behavior).
"""

from typing import Optional, Protocol

from PySide6.QtWidgets import QWidget


class UiLoader(Protocol):
    """
    Protocol for loading Qt Designer .ui files at runtime.

    Implementations should expose a load() method returning the instantiated
    widget hierarchy. They may optionally accept an existing base instance
    to populate, depending on the widget type (QMainWindow/QDialog/etc.).
    """

    def load(self, ui_path: str, baseinstance: Optional[WIDGET] = None) -> QWidget:
        """
        Load a .ui file and return the root widget.

        Args:
            ui_path: Relative path to the .ui file (see UiFiles in paths.py).
            baseinstance: Optional existing instance of a Qt base class to populate.

        Returns:
            The root widget that was created from the .ui file.
        """
        raise NotImplementedError


class QtDesignerUiLoader:
    """
    Placeholder implementation that will use Qt's runtime loading (e.g., QUiLoader)
    once implemented.

    Responsibilities:
    - Resolve ui_path (string) to an accessible resource/file.
    - Handle custom/promoted widgets (e.g., TrafficCanvasView).
    - Populate baseinstance when provided.
    - Return the created widget tree for binding.
    """

    def __init__(self):
        """
        Initialize loader state, such as custom widget factories or mappings.
        """
        pass

    def load(self, ui_path: str, baseinstance: Optional[WIDGET] = None) -> QWidget:
        """
        Load and return the widget hierarchy from a .ui file.

        Implementation notes:
        - Use PySide6.QtUiTools.QUiLoader with QFile to load ui_path.
        - If you have promoted widgets, register them so the loader can instantiate
          the correct classes.
        - Validate that the resulting root widget matches the expected type.

        Returns:
            The root widget built from the .ui file.
        """
        raise NotImplementedError
