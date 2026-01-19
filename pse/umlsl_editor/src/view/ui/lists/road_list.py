"""
Road list controller for the UMLSL Traffic Editor.

Manages the list widget displaying all road entities.
"""
from pse.umlsl_editor.src.view.ui.dialogs.road_edit_dialog import RoadEditDialog
from pse.umlsl_editor.src.view.ui.lists.list_controller import ListController


class RoadListController(ListController):
    """Controller for the road entity list."""

    def __init__(self, main_ui):
        """
        Initialize the road list controller.

        Args:
            main_ui: Reference to the main UI widget.
        """
        super().__init__(
            main_ui,
            "list_roads",
            RoadEditDialog
        )

    def setup_row_ui(self, row_widget, road) -> None:
        """
        Populate a row widget with road data.

        Args:
            row_widget: The widget for this row.
            road: The Road entity to display.
        """
        # TODO: Implement road row population
        pass