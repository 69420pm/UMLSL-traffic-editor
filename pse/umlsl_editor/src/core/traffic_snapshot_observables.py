from typing import TypeVar, MutableMapping, Iterator, MutableSequence

from pse.umlsl_editor.src.core.traffic_snapshot_event_manager import TrafficSnapshotEventType, \
    TrafficSnapshotEventManager

Key = TypeVar("Key")
Value = TypeVar("Value")
T = TypeVar("T")


class ObservableDict(MutableMapping[Key, Value]):
    """
    A dictionary that notifies an event manager on additions, removals, and updates.
    """
    def __init__(
            self,
            event_manager: TrafficSnapshotEventManager,
            add_event: TrafficSnapshotEventType,
            remove_event: TrafficSnapshotEventType,
            update_event: TrafficSnapshotEventType,
            initial_data: dict[Key, Value] | None = None,
    ):
        raise NotImplementedError

    def __setitem__(self, key: Key, value: Value) -> None:
        raise NotImplementedError

    def __delitem__(self, key: Key) -> None:
        raise NotImplementedError

    def __getitem__(self, key: Key) -> Value:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Key]:
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError


class ObservableList(MutableSequence[T]):
    """
    A list that notifies an event manager on additions, removals, and updates.
    """
    def __init__(
            self,
            event_manager: TrafficSnapshotEventManager,
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

