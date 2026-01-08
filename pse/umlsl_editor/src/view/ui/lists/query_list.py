from pse.umlsl_editor.src.view.ui.dialogs.query_edit_dialog import QueryEditDialog
from pse.umlsl_editor.src.view.ui.lists.list_controller import ListController


class QueryListController(ListController):
    def __init__(self, main_ui):
        super().__init__(
            main_ui,
            "Queries",
            QueryEditDialog
        )

    def setup_row_ui(self, row_widget, road):
        pass