"""
Car list controller for the UMLSL Traffic Editor.

Manages the list widget displaying all car entities.
"""
from pse.umlsl_editor.src.view.ui.dialogs.car_edit_dialog import CarEditDialog
from pse.umlsl_editor.src.view.ui.lists.list_controller import ListController


class CarListController(ListController):
    """Controller for the car entity list."""

    def __init__(self, main_ui):
        """
        Initialize the car list controller.

        Args:
            main_ui: Reference to the main UI widget.
        """
        super().__init__(
            main_ui=main_ui,
            list_widget_name="Cars",
            edit_dialog_class=CarEditDialog
        )

    def setup_row_ui(self, row_widget, car) -> None:
        """
        Populate a row widget with car data.

        Args:
            row_widget: The widget for this row.
            car: The Car entity to display.
        """
        # TODO: Implement car row population
        pass