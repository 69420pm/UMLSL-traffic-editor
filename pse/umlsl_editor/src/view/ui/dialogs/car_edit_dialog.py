"""
Car editing dialog for the UMLSL Traffic Editor.

Provides a dialog for creating and editing car entities.
"""
from pse.umlsl_editor.src.view.ui.dialogs.editor_dialog_controller import EditDialog


class CarEditDialog(EditDialog):
    """Dialog for editing car entity properties."""

    def __init__(self, *args, **kwargs):
        """Initialize the car edit dialog."""
        super().__init__(*args)

    def load_data_into_ui(self) -> None:
        """Populate UI fields with car data."""
        # TODO: Implement car data loading
        pass

    def get_data_from_ui(self):
        """
        Read UI fields and create an updated Car entity.

        Returns:
            Updated Car entity, or None if validation fails.
        """
        # TODO: Implement car data reading
        pass