"""
Deletion confirmation dialog for the UMLSL Traffic Editor.

Provides a confirmation dialog before deleting entities.
"""


class DeletionConfirmationDialog:
    """Dialog for confirming entity deletion."""

    def __init__(self, confirmation_text: str):
        """
        Initialize the deletion confirmation dialog.

        Args:
            confirmation_text: Text describing what will be deleted.
        """
        self.confirmation_text = confirmation_text

    def setup_ui(self) -> None:
        """Set up the confirmation dialog UI."""
        # TODO: Implement confirmation dialog UI
        pass

    def on_delete(self) -> None:
        """Handle delete confirmation."""
        # TODO: Implement delete action
        pass

    def on_cancel(self) -> None:
        """Handle cancel action."""
        pass