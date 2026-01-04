"""
Widget for displaying a list of roads with their properties.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal

from pse.umlsl_editor.src.core.dataclasses.road import Road


class RoadsListWidget(QWidget):
    """
    Widget that displays a list of roads with their key properties.
    """

    # Signal emitted when a road is selected
    road_selected = Signal(Road)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._roads = {}  # Map road ID to (Road, QListWidgetItem)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_item_clicked)

        layout.addWidget(self.list_widget)

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click events."""
        road_id = item.data(0x0100)  # UserRole
        if road_id in self._roads:
            road, _ = self._roads[road_id]
            self.road_selected.emit(road)

    def add_road(self, road: Road) -> None:
        """Add a road to the list."""
        if road.name in self._roads:
            return

        item = QListWidgetItem()
        item.setText(self._format_road_text(road))
        item.setData(0x0100, road.name)  # Store road ID in UserRole

        self.list_widget.addItem(item)
        self._roads[road.name] = (road, item)

    def remove_road(self, road: Road) -> None:
        """Remove a road from the list."""
        if road.name not in self._roads:
            return

        _, item = self._roads[road.name]
        row = self.list_widget.row(item)
        self.list_widget.takeItem(row)
        del self._roads[road.name]

    def update_road(self, road: Road) -> None:
        """Update a road's display in the list."""
        if road.name not in self._roads:
            return

        _, item = self._roads[road.name]
        item.setText(self._format_road_text(road))
        self._roads[road.name] = (road, item)

    def _format_road_text(self, road: Road) -> str:
        """Format road data for display."""
        lanes_info = f"{road.forward_lanes}↑ {road.backward_lanes}↓"
        orientation = "H" if road.orientation.value == "horizontal" else "V"
        return f"{road.name} - {lanes_info} - {orientation} @ {road.position:.1f}"

