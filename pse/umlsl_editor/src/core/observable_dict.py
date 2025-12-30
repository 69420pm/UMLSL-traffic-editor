"""Observable dictionary that emits PyQt6 signals on mutations."""

from typing import TypeVar, Generic, Iterator, MutableMapping
from PyQt6.QtCore import QObject, pyqtSignal

K = TypeVar('K')
V = TypeVar('V')


class ObservableDict(QObject, MutableMapping[K, V], Generic[K, V]):
    """
    A dictionary wrapper that emits PyQt6 signals when items are added, removed, or updated.

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
        self._data: dict[K, V] = dict(initial_data) if initial_data else {}
        self._batch_mode: bool = False
        self._batch_operations: list[tuple[str, tuple]] = []

    def __setitem__(self, key: K, value: V) -> None:
        if key in self._data:
            old_value = self._data[key]
            self._data[key] = value
            if self._batch_mode:
                self._batch_operations.append(('updated', (key, old_value, value)))
            else:
                self.item_updated.emit(key, old_value, value)
        else:
            self._data[key] = value
            if self._batch_mode:
                self._batch_operations.append(('added', (key, value)))
            else:
                self.item_added.emit(key, value)

    def __delitem__(self, key: K) -> None:
        value = self._data.pop(key)
        if self._batch_mode:
            self._batch_operations.append(('removed', (key, value)))
        else:
            self.item_removed.emit(key, value)

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def clear(self) -> None:
        """Remove all items and emit cleared signal."""
        self._data.clear()
        if self._batch_mode:
            self._batch_operations.append(('cleared', ()))
        else:
            self.cleared.emit()

    def pop(self, key: K, *args) -> V:
        """Remove and return value, emitting item_removed signal."""
        if key in self._data:
            value = self._data.pop(key)
            if self._batch_mode:
                self._batch_operations.append(('removed', (key, value)))
            else:
                self.item_removed.emit(key, value)
            return value
        elif args:
            return args[0]
        else:
            raise KeyError(key)

    def update(self, other=None, **kwargs) -> None:
        """Update dictionary, emitting appropriate signals for each item."""
        if other:
            items = other.items() if hasattr(other, 'items') else other
            for key, value in items:
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def setdefault(self, key: K, default: V = None) -> V:
        """Set default value if key doesn't exist, emitting item_added if added."""
        if key not in self._data:
            self[key] = default
        return self._data[key]

    def batch_update(self) -> 'BatchContext[K, V]':
        """
        Context manager for batch updates. Signals are deferred until exit.

        Usage:
            with observable_dict.batch_update():
                observable_dict["a"] = 1
                observable_dict["b"] = 2
            # Signals emitted here
        """
        return BatchContext(self)

    def _emit_batch_operations(self) -> None:
        """Emit all deferred signals from batch mode."""
        for operation, args in self._batch_operations:
            if operation == 'added':
                self.item_added.emit(*args)
            elif operation == 'removed':
                self.item_removed.emit(*args)
            elif operation == 'updated':
                self.item_updated.emit(*args)
            elif operation == 'cleared':
                self.cleared.emit()
        self._batch_operations.clear()


class BatchContext(Generic[K, V]):
    """Context manager for batch updates to ObservableDict."""

    def __init__(self, observable_dict: ObservableDict[K, V]):
        self._dict = observable_dict

    def __enter__(self) -> 'BatchContext[K, V]':
        self._dict._batch_mode = True
        self._dict._batch_operations = []
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self._dict._batch_mode = False
        if exc_type is None:
            self._dict._emit_batch_operations()
        else:
            self._dict._batch_operations.clear()

