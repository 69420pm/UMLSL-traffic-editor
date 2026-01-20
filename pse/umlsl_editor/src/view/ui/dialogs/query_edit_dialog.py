"""
Query editing dialog for the UMLSL Traffic Editor.

Provides a dialog for creating and editing UMLSL query entities.
"""
from pse.umlsl_editor.src.view.ui.dialogs.editor_dialog_controller import EditDialog


class QueryEditDialog(EditDialog):
    """Dialog for editing UMLSL query properties."""

    def __init__(self, *args, **kwargs):
        """Initialize the query edit dialog."""
        super().__init__(*args)

    def load_data_into_ui(self) -> None:
        """Populate UI fields with query data."""
        # TODO: Implement query data loading
        pass

    def get_data_from_ui(self):
        """
        Read UI fields and create an updated query entity.

        Returns:
            Updated query entity, or None if validation fails.
        """
        # TODO: Implement query data reading
        pass