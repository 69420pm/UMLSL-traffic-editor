"""
Widget for displaying a list of UMLSL queries with their properties.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal

from pse.umlsl_editor.src.core.dataclasses.umlsl_query import UMLSLQuery


class QueriesListWidget(QWidget):
    """
    Widget that displays a list of UMLSL queries with their key properties.
    """

    # Signal emitted when a query is selected
    query_selected = Signal(UMLSLQuery)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._queries = {}  # Map query hash to (UMLSLQuery, QListWidgetItem)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.list_widget)

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click events."""
        query_hash = item.data(0x0100)  # UserRole
        if query_hash in self._queries:
            query, _ = self._queries[query_hash]
            self.query_selected.emit(query)

    def add_query(self, query: UMLSLQuery) -> None:
        """Add a query to the list."""
        query_hash = hash((query.latex, query.assigned_car.name))
        if query_hash in self._queries:
            return

        item = QListWidgetItem()
        item.setText(self._format_query_text(query))
        item.setData(0x0100, query_hash)  # Store query hash in UserRole

        self.list_widget.addItem(item)
        self._queries[query_hash] = (query, item)

    def remove_query(self, query: UMLSLQuery) -> None:
        """Remove a query from the list."""
        query_hash = hash((query.latex, query.assigned_car.name))
        if query_hash not in self._queries:
            return

        _, item = self._queries[query_hash]
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        del self._queries[query_hash]

    def update_query(self, query: UMLSLQuery) -> None:
        """Update a query's display in the list."""
        query_hash = hash((query.latex, query.assigned_car.name))
        if query_hash not in self._queries:
            return

        _, item = self._queries[query_hash]
        item.setText(self._format_query_text(query))
        self._queries[query_hash] = (query, item)

    def _format_query_text(self, query: UMLSLQuery) -> str:
        """Format query data for display."""
        status = "✓" if query.validation else "✗"
        latex_preview = query.latex[:40] + "..." if len(query.latex) > 40 else query.latex
        return f"{status} {query.assigned_car.name}: {latex_preview}"

