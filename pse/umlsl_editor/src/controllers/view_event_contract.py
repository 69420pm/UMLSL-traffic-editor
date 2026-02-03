"""Interface for handling view events from the event controller."""
from abc import abstractmethod

from PySide6.QtCore import SignalInstance, QObject

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery
from pse.umlsl_editor.src.model.errors.errors import BaseWarning
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


class ViewEventHandler(QObject):
    """
    Abstract interface for handling model change events in the view layer.

    This interface defines all methods that the view must implement to respond
    to changes in the model (TrafficSnapshot, Settings, UMLSLQueries).
    The EventController will call these methods when it receives events from the observable models.
    """

    # Car-related events
    @abstractmethod
    def add_car_view(self, car: Car) -> None:
        """
        Handle the addition of a car to the traffic snapshot.

        Args:
            car: The car entity that was added.
        """
        pass

    @abstractmethod
    def remove_car_view(self, car: Car) -> None:
        """
        Handle the removal of a car from the traffic snapshot.

        Args:
            car: The car entity that was removed.
        """
        pass

    @abstractmethod
    def update_car_view(self, car: Car) -> None:
        """
        Handle the update of a car in the traffic snapshot.

        Args:
            car: The car entity that was updated.
        """
        pass

    # Road-related events
    @abstractmethod
    def add_road_view(self, road: Road) -> None:
        """
        Handle the addition of a road to the traffic snapshot.

        Args:
            road: The road entity that was added.
        """
        pass

    @abstractmethod
    def remove_road_view(self, road: Road) -> None:
        """
        Handle the removal of a road from the traffic snapshot.

        Args:
            road: The road entity that was removed.
        """
        pass

    @abstractmethod
    def update_road_view(self, road: Road) -> None:
        """
        Handle the update of a road in the traffic snapshot.

        Args:
            road: The road entity that was updated.
        """
        pass

    # # Crossing segment-related events
    # @abstractmethod
    # def add_crossing_segment_view(self, crossing_segment: CrossingSegment) -> None:
    #     """
    #     Handle the addition of a crossing segment to the traffic snapshot.
    #
    #     Args:
    #         crossing_segment: The crossing segment that was added.
    #     """
    #     pass
    #
    # @abstractmethod
    # def remove_crossing_segment_view(self, crossing_segment: CrossingSegment) -> None:
    #     """
    #     Handle the removal of a crossing segment from the traffic snapshot.
    #
    #     Args:
    #         crossing_segment: The crossing segment that was removed.
    #     """
    #     pass
    #
    # @abstractmethod
    # def update_crossing_segment_view(self, crossing_segment: CrossingSegment) -> None:
    #     """
    #     Handle the update of a crossing segment in the traffic snapshot.
    #
    #     Args:
    #         crossing_segment: The crossing segment that was updated.
    #     """
    #     pass

    # UMLSL Query-related events
    @abstractmethod
    def add_query_view(self, query: UMLSLQuery) -> None:
        """
        Handle the addition of a UMLSL query.

        Args:
            query: The UMLSL query that was added.
        """
        pass

    @abstractmethod
    def remove_query_view(self, query: UMLSLQuery) -> None:
        """
        Handle the removal of a UMLSL query.

        Args:
            query: The UMLSL query that was removed.
        """
        pass

    @abstractmethod
    def update_query_view(self, query: UMLSLQuery) -> None:
        """
        Handle the update of a UMLSL query.

        Args:
            query: The UMLSL query that was updated.
        """
        pass

    # Settings-related events
    @abstractmethod
    def change_breaking_acceleration(self, breaking_acceleration: float) -> None:
        """
        Handle the change of breaking acceleration setting.

        Args:
            breaking_acceleration: The new breaking acceleration value.
        """
        pass

    @abstractmethod
    def toggle_coordinate_system(self, render_coordinate_system: bool) -> None:
        """
        Handle the toggle of coordinate system rendering.

        Args:
            render_coordinate_system: Whether to render the coordinate system.
        """
        pass

    @abstractmethod
    def toggle_safety_distance(self, render_safety_distance: bool) -> None:
        """
        Handle the toggle of safety distance rendering.

        Args:
            render_safety_distance: Whether to render safety distances.
        """
        pass

    @abstractmethod
    def get_on_selection_changed_signal(self) -> "SignalInstance":
        """
        Returns a signal that is emitted when an entity is selected.
        The signal should carry the UID of the selected entity as a string.
        """
        pass

    @abstractmethod
    def get_current_selected_uid(self) -> str:
        """
        Returns the UID of the currently selected entity.
        """
        pass

    @abstractmethod
    def entity_selected_view(self, uid: str) -> None:
        """
        Handle the selection of an entity.

        Args:
            uid: The uid of entity that was selected.
        """
        pass

    @abstractmethod
    def display_warning(self, warning: BaseWarning):
        """
        Handle the display of a warning message.
        Args:
            warning: The warning message to be displayed.
        """
        pass

    @abstractmethod
    def refresh_all_segments_view(self, segments: list[Segment]):
        pass
