"""
Global controls for the UMLSL Traffic Editor.

Handles save, load, and other global application actions.
"""


class GlobalControls:
    """
    Controller for global application actions.

    Manages file operations (save, load) and other global controls.
    """

    def __init__(self, main_ui):
        """
        Initialize global controls.

        Args:
            main_ui: Reference to the main UI widget.
        """
        self.main_ui = main_ui

    def setup_ui(self) -> None:
        """Set up UI connections for global controls."""
        pass

    def on_save(self) -> None:
        """Handle save action."""
        pass

    def on_save_as(self) -> None:
        """Handle save-as action."""
        pass

    def on_load(self) -> None:
        """Handle load action."""
        pass