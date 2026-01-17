"""
Query list controller for the UMLSL Traffic Editor.

Manages the list widget displaying all UMLSL query entities.
"""
from pse.umlsl_editor.src.view.ui.dialogs.query_edit_dialog import QueryEditDialog
from pse.umlsl_editor.src.view.ui.lists.list_controller import ListController


class QueryListController(ListController):
    """Controller for the UMLSL query list."""

    def __init__(self, main_ui):
        """
        Initialize the query list controller.

        Args:
            main_ui: Reference to the main UI widget.
        """
        super().__init__(
            main_ui,
            "Queries",
            QueryEditDialog
        )

    def setup_row_ui(self, row_widget, query) -> None:
        """
        Populate a row widget with query data.

        Args:
            row_widget: The widget for this row.
            query: The query entity to display.
        """
        # TODO: Implement query row population
        pass