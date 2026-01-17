"""
Error dialog for the UMLSL Traffic Editor.

Provides a dialog for displaying error messages to the user.
"""


class ErrorDialog:
    """Dialog for displaying error messages."""

    def __init__(self, error_title: str, error_message: str):
        """
        Initialize the error dialog.

        Args:
            error_title: Title of the error dialog.
            error_message: Detailed error message to display.
        """
        self.error_title = error_title
        self.error_message = error_message

    def setup_ui(self) -> None:
        """Set up the error dialog UI."""
        # TODO: Implement error dialog UI
        pass

    def on_close(self) -> None:
        """Handle dialog close event."""
        pass