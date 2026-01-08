from pse.umlsl_editor.src.view.ui.dialogs.road_edit_dialog import RoadEditDialog
from pse.umlsl_editor.src.view.ui.lists.list_controller import ListController


class RoadListController(ListController):
    def __init__(self, main_ui):
        super().__init__(
            main_ui,
            "list_roads",
            RoadEditDialog
        )

    def setup_row_ui(self, row_widget, road):
        pass