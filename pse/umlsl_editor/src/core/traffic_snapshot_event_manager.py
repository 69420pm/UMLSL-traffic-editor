from collections.abc import Callable, Iterator, MutableMapping, MutableSequence
from enum import Enum
from typing import Any, Generic, Literal, TypeVar, overload, TYPE_CHECKING

if TYPE_CHECKING:
    from pse.umlsl_editor.src.core.dataclasses.car import Car
    from pse.umlsl_editor.src.core.dataclasses.road import Road


class TrafficSnapshotEventType(Enum):
    """
    Defines the types of events that can occur within the TrafficSnapshot.
    """
    CAR_ADDED = "car_added"
    CAR_REMOVED = "car_removed"
    CAR_SELECTED = "car_selected"
    CAR_DESELECTED = "car_deselected"
    CAR_UPDATED = "car_updated"

    ROAD_ADDED = "road_added"
    ROAD_REMOVED = "road_removed"
    ROAD_SELECTED = "road_selected"
    ROAD_DESELECTED = "road_deselected"
    ROAD_UPDATED = "road_updated"

    UPDATE_UMLSL_QUERY = "update_umlsl_query"

    NEW_TRAFFIC_SNAPSHOT_LOADED = "new_traffic_snapshot_loaded"
    """A new TrafficSnapshot has been loaded into the application and the entire state may have changed."""

    SELECTION_CLEARED = "selection_cleared"


class TrafficSnapshotEventManager:
    """
    Manages subscriptions and notifications for changes in the TrafficSnapshot.
    """
    def __init__(self):
        self.subscribers: dict[TrafficSnapshotEventType, list[Callable[[Any], None]]] = {}

    @overload
    def subscribe(
        self,
        event_type: Literal[
            TrafficSnapshotEventType.CAR_ADDED,
            TrafficSnapshotEventType.CAR_REMOVED,
            TrafficSnapshotEventType.CAR_SELECTED,
            TrafficSnapshotEventType.CAR_DESELECTED,
            TrafficSnapshotEventType.CAR_UPDATED,
        ],
        callback: Callable[["Car"], None],
    ) -> None:
        raise NotImplementedError

    @overload
    def subscribe(
        self,
        event_type: Literal[
            TrafficSnapshotEventType.ROAD_ADDED,
            TrafficSnapshotEventType.ROAD_REMOVED,
            TrafficSnapshotEventType.ROAD_SELECTED,
            TrafficSnapshotEventType.ROAD_DESELECTED,
            TrafficSnapshotEventType.ROAD_UPDATED,
        ],
        callback: Callable[["Road"], None],
    ) -> None:
        raise NotImplementedError

    def subscribe(self, event_type: TrafficSnapshotEventType, callback: Callable[[Any], None]) -> None:
        """
        Registers a callback function to be executed when a specific event occurs.

        Args:
            event_type: The specific TrafficSnapshotEventType to listen for.
            callback: A function that accepts a single argument (the data associated with the event).
                      - For CAR_* events, the data is the 'Car' object.
                      - For ROAD_* events, the data is the 'Road' object.
        """
        raise NotImplementedError

    @overload
    def unsubscribe(
        self,
        event_type: Literal[
            TrafficSnapshotEventType.CAR_ADDED,
            TrafficSnapshotEventType.CAR_REMOVED,

            TrafficSnapshotEventType.CAR_UPDATED,
        ],
        callback: Callable[["Car"], None],
    ) -> None:
        raise NotImplementedError

    @overload
    def unsubscribe(
        self,
        event_type: Literal[
            TrafficSnapshotEventType.ROAD_ADDED,
            TrafficSnapshotEventType.ROAD_REMOVED,
            TrafficSnapshotEventType.ROAD_UPDATED,
        ],
        callback: Callable[["Road"], None],
    ) -> None:
        raise NotImplementedError

    def unsubscribe(self, event_type: TrafficSnapshotEventType, callback: Callable[[Any], None]) -> None:
        """
        Removes a previously registered callback for a specific event type.
        """
        raise NotImplementedError

    @overload
    def notify(
        self,
        event_type: Literal[
            TrafficSnapshotEventType.CAR_ADDED,
            TrafficSnapshotEventType.CAR_REMOVED,
            TrafficSnapshotEventType.CAR_UPDATED,
        ],
        data: "Car",
    ) -> None:
        raise NotImplementedError

    @overload
    def notify(
        self,
        event_type: Literal[
            TrafficSnapshotEventType.ROAD_ADDED,
            TrafficSnapshotEventType.ROAD_REMOVED,
            TrafficSnapshotEventType.ROAD_UPDATED,
        ],
        data: "Road",
    ) -> None:
        raise NotImplementedError

    def notify(self, event_type: TrafficSnapshotEventType, data: Any) -> None:
        """
        Notifies all subscribers of a specific event type.

        Args:
            event_type: The type of event that occurred.
            data: The entity associated with the event (e.g., the Car or Road instance).
                  This allows the View to know exactly which object was added/removed/updated
                  without searching the entire snapshot.
        """
        raise NotImplementedError


K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


class ObservableDict(MutableMapping[K, V]):
    def __init__(
        self,
        event_manager: "TrafficSnapshotEventManager",
        add_event: TrafficSnapshotEventType,
        remove_event: TrafficSnapshotEventType,
        update_event: TrafficSnapshotEventType,
        initial_data: dict[K, V] | None = None,
    ):
        raise NotImplementedError

    def __setitem__(self, key: K, value: V) -> None:
        raise NotImplementedError

    def __delitem__(self, key: K) -> None:
        raise NotImplementedError

    def __getitem__(self, key: K) -> V:
        raise NotImplementedError

    def __iter__(self) -> Iterator[K]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class ObservableList(MutableSequence[T]):
    def __init__(
        self,
        event_manager: "TrafficSnapshotEventManager",
        add_event: TrafficSnapshotEventType,
        remove_event: TrafficSnapshotEventType,
        update_event: TrafficSnapshotEventType,
        initial_data: list[T] | None = None,
    ):
        raise NotImplementedError

    def insert(self, index: int, value: T) -> None:
        raise NotImplementedError

    def __getitem__(self, index: int) -> T:
        raise NotImplementedError

    def __setitem__(self, index: int, value: T) -> None:
        raise NotImplementedError

    def __delitem__(self, index: int) -> None:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

