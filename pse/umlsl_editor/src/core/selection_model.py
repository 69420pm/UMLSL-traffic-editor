from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.dataclasses.road import Road


class SelectionModel:
    """A model to manage selection of cars and roads in a traffic simulation."""
    def __init__(self):
        self._selected_car: Car | None = None
        self._selected_road: Road | None = None

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