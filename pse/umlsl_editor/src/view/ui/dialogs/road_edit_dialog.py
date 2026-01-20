"""
Road editing dialog for the UMLSL Traffic Editor.

Provides a dialog for creating and editing road entities.
"""
from pse.umlsl_editor.src.view.ui.dialogs.editor_dialog_controller import EditDialog


class RoadEditDialog(EditDialog):
    """Dialog for editing road entity properties."""

    def __init__(self, *args, **kwargs):
        """Initialize the road edit dialog."""
        super().__init__(*args)

    def load_data_into_ui(self) -> None:
        """Populate UI fields with road data."""
        # TODO: Implement road data loading
        pass

    def get_data_from_ui(self):
        """
        Read UI fields and create an updated Road entity.

        Returns:
            Updated Road entity, or None if validation fails.
        """
        # TODO: Implement road data reading
        pass