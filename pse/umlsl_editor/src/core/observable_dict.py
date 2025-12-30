from typing import TypeVar, Generic, Iterator, MutableMapping
from PyQt6.QtCore import QObject, pyqtSignal

K = TypeVar('K')
V = TypeVar('V')


class ObservableDict(QObject, MutableMapping[K, V], Generic[K, V]):
    """
    A dictionary wrapper that emits PyQt6 signals when items are added, removed, or updated.
    Its purpose is to allow the view which uses PyQt6 to react to changes directly from a dictionary,
    without having to emit manual a signal whenever the dictionary gets updated.

    Signals:
        item_added(key, value): Emitted when a new key-value pair is added.
        item_removed(key, value): Emitted when a key-value pair is removed.
        item_updated(key, old_value, new_value): Emitted when an existing key's value is updated.
        cleared(): Emitted when the dictionary is cleared.

    Usage:
        cars = ObservableDict[str, Car]()
        cars.item_added.connect(lambda k, v: print(f"Added {k}: {v}"))
        cars["car1"] = Car(...)  # Emits item_added
    """

    # Signals use object type since PyQt signals don't support generics
    item_added = pyqtSignal(object, object)  # (key, value)
    item_removed = pyqtSignal(object, object)  # (key, value)
    item_updated = pyqtSignal(object, object, object)  # (key, old_value, new_value)
    cleared = pyqtSignal()

    def __init__(self, initial_data: dict[K, V] | None = None, parent: QObject | None = None):
        """
        Initialize the ObservableDict.

        Args:
            initial_data: Optional dictionary to initialize with (no signals emitted for initial data).
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        # TODO: Initialize internal dictionary to store data
        # TODO: Store initial_data if provided

    def __setitem__(self, key: K, value: V) -> None:
        """
        Set an item in the dictionary.

        Implementation plan:
        - Check if key already exists
        - If exists, emit item_updated signal with old and new value
        - If new, emit item_added signal
        - Store the key-value pair in internal dictionary
        """
        pass

    def __delitem__(self, key: K) -> None:
        """
        Delete an item from the dictionary.

        Implementation plan:
        - Remove the key from internal dictionary
        - Emit item_removed signal with key and value
        """
        pass

    def __getitem__(self, key: K) -> V:
        """
        Get an item from the dictionary.

        Implementation plan:
        - Return value from internal dictionary for the given key
        """
        pass

    def __len__(self) -> int:
        """
        Return the number of items in the dictionary.

        Implementation plan:
        - Return length of internal dictionary
        """
        pass

    def __iter__(self) -> Iterator[K]:
        """
        Return an iterator over dictionary keys.

        Implementation plan:
        - Return iterator from internal dictionary
        """
        pass

    def __contains__(self, key: object) -> bool:
        """
        Check if key exists in the dictionary.

        Implementation plan:
        - Check if key exists in internal dictionary
        """
        pass

    def clear(self) -> None:
        """
        Remove all items and emit cleared signal.

        Implementation plan:
        - Clear internal dictionary
        - Emit cleared signal
        """
        pass

    def pop(self, key: K, *args) -> V:
        """
        Remove and return value, emitting item_removed signal.

        Implementation plan:
        - Check if key exists
        - If exists, pop from internal dictionary and emit item_removed signal
        - If not exists and default provided, return default
        - If not exists and no default, raise KeyError
        """
        pass

    def update(self, other=None, **kwargs) -> None:
        """
        Update dictionary, emitting appropriate signals for each item.

        Implementation plan:
        - Iterate over items from other dict or kwargs
        - For each item, call __setitem__ to trigger appropriate signals
        """
        pass

    def setdefault(self, key: K, default: V = None) -> V:
        """
        Set default value if key doesn't exist, emitting item_added if added.

        Implementation plan:
        - Check if key exists
        - If not exists, set it to default value (will emit item_added)
        - Return the value (existing or newly set)
        """
        pass

