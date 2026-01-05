"""
Widget for displaying a list of cars with their properties.
"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QListWidgetItem
from PySide6.QtCore import Signal

from pse.umlsl_editor.src.core.dataclasses.car import Car


class CarsListWidget(QWidget):
    """
    Widget that displays a list of cars with their key properties.
    """

    # Signal emitted when a car is selected
    car_selected = Signal(Car)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cars = {}  # Map car ID to (Car, QListWidgetItem)
        self._setup_ui()

    def _setup_ui(self):
        """Initialize the UI components."""
        # layout = QVBoxLayout(self)
        #
        # self.list_widget = QListWidget()
        # self.list_widget.itemClicked.connect(self._on_item_clicked)
        #
        # layout.addWidget(self.list_widget)

    def _on_item_clicked(self, item: QListWidgetItem):
        """Handle item click events."""
        # car_id = item.data(0x0100)  # UserRole
        # if car_id in self._cars:
        #     car, _ = self._cars[car_id]
        #     self.car_selected.emit(car)
        #     # Enable edit/delete buttons when an item is selected
        #     self.edit_button.setEnabled(True)
        #     self.delete_button.setEnabled(True)

    def _on_add_clicked(self):
        """Handle add button click."""
        # self.create_car_requested.emit()

    def _on_edit_clicked(self):
        """Handle edit button click."""
        # current_item = self.list_widget.currentItem()
        # if current_item:
        #     car_name = current_item.data(0x0100)
        #     self.edit_car_requested.emit(car_name)

    def _on_delete_clicked(self):
        """Handle delete button click."""
        # current_item = self.list_widget.currentItem()
        # if current_item:
        #     car_name = current_item.data(0x0100)
        #     self.delete_car_requested.emit(car_name)

    def add_car(self, car: Car) -> None:
        """Add a car to the list."""
        # if car.name in self._cars:
        #     return
        #
        # item = QListWidgetItem()
        # item.setText(self._format_car_text(car))
        # item.setData(0x0100, car.name)  # Store car ID in UserRole
        #
        # self.list_widget.addItem(item)
        # self._cars[car.name] = (car, item)

    def remove_car(self, car: Car) -> None:
        """Remove a car from the list."""
        # if car.name not in self._cars:
        #     return
        #
        # _, item = self._cars[car.name]
        # row = self.list_widget.row(item)
        # self.list_widget.takeItem(row)
        # del self._cars[car.name]

    def update_car(self, car: Car) -> None:
        """Update a car's display in the list."""
        # if car.name not in self._cars:
        #     return
        #
        # _, item = self._cars[car.name]
        # item.setText(self._format_car_text(car))
        # self._cars[car.name] = (car, item)

    def _format_car_text(self, car: Car) -> str:
        """Format car data for display."""
        # return f"{car.name} - Lane {car.lane.lane_index} ({car.lane.lane_direction.value}) - {car.velocity:.1f} m/s"

