from dataclasses import dataclass

from PySide6.QtCore import Signal, QObject

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road


@dataclass
class Selection(QObject):
    """A model to manage selection of cars and roads in a traffic simulation."""
    selected_car: Car | None = None
    selected_road: Road | None = None

    select_car_signal = Signal()
    deselect_car_signal = Signal()
    select_road_signal = Signal()
    deselect_road_signal = Signal()
    clear_selection_signal = Signal()

    def select_car(self, car: Car) -> None:
        """Selects a single car by its ID and deselects every other car and all roads."""
        raise NotImplementedError

    def deselect_car(self, car: Car) -> None:
        """Deselects a single car by its ID."""
        raise NotImplementedError

    def select_road(self, road: Road) -> None:
        """Selects a single road by its ID and deselects every other road and all cars."""
        raise NotImplementedError

    def deselect_road(self, road: Road) -> None:
        """Deselects a single road by its ID."""
        raise NotImplementedError

    def clear_selection(self) -> None:
        """Clears the selection of all cars and roads."""
        raise NotImplementedError