from typing import TypeVar, MutableMapping, Iterator, MutableSequence, Callable, Optional

Key = TypeVar("Key")
Value = TypeVar("Value")
T = TypeVar("T")


class ObservableDict(MutableMapping[Key, Value]):
    """
    A dictionary that notifies via callbacks on additions, removals, and updates.
    Can be used with PySide signals by passing signal.emit as the callback.
    """
    def __init__(
            self,
            on_add: Optional[Callable[[Value], None]] = None,
            on_remove: Optional[Callable[[Value], None]] = None,
            on_update: Optional[Callable[[Value], None]] = None,
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
    A list that notifies via callbacks on additions, removals, and updates.
    """
    def __init__(
            self,
            on_add: Optional[Callable[[T], None]] = None,
            on_remove: Optional[Callable[[T], None]] = None,
            on_update: Optional[Callable[[T], None]] = None,
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

