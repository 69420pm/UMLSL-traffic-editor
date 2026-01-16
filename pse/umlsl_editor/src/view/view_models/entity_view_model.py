from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPolygonF, QPainterPath

# Generic type variable to indicate what kind of data this model holds (Car, Road, etc.)
T = TypeVar('T')


class EntityViewModel(ABC, Generic[T]):
    """
    Abstract base class for all traffic entities.
    Ensures that Cars, Roads, and Crossings all implement the drawing contract.
    """

    def __init__(self, entity_data: T):
        self._data = entity_data

        # Cache for geometry
        self._bounding_rect = QRectF()
        self._shape = QPainterPath()  # or QPolygonF
        self._color = QColor()

        # Initial calculation
        self.recalculate()

    @property
    def data(self) -> T:
        """Returns the raw domain entity (e.g. the Car instance)."""
        return self._data

    def update(self, entity_data: T):
        """Standard method to push new data into the view model."""
        self._data = entity_data
        self.recalculate()

    @abstractmethod
    def recalculate(self):
        """
        Force recalculation of geometry (x, y, polygons).
        Must be implemented by child classes.
        """
        pass

    # --- Graphics Interface (Used by QGraphicsItem) ---

    @property
    def bounding_rect(self) -> QRectF:
        """Returns the outer bounds of the item (fast collision/culling)."""
        return self._bounding_rect

    @property
    def shape(self) -> QPainterPath:
        """Returns the precise shape of the item (for drawing/collision)."""
        return self._shape

    @property
    def color(self) -> QColor:
        """Returns the color to paint."""
        return self._color