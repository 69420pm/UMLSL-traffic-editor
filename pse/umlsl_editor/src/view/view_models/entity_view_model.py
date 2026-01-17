"""
Base view model for traffic entities.

Provides an abstract base class for view models that bridge domain entities
with their graphical representations.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainterPath

T = TypeVar('T')


class EntityViewModel(ABC, Generic[T]):
    """
    Abstract base class for all traffic entity view models.

    Ensures that Cars, Roads, and Crossings all implement the drawing contract.
    Provides common properties for geometry and color.
    """

    def __init__(self, entity_data: T):
        """
        Initialize the view model with entity data.

        Args:
            entity_data: The domain entity (Car, Road, CrossingSegment, etc.)
        """
        self._border_color = QColor()
        self._data = entity_data

        # Geometry cache
        self._bounding_rect = QRectF()
        self._shape = QPainterPath()
        self._color = QColor()

        # Calculate initial geometry
        self.recalculate()

    @property
    def data(self) -> T:
        """Return the raw domain entity."""
        return self._data

    def update(self, entity_data: T) -> None:
        """
        Update the view model with new entity data.

        Args:
            entity_data: The updated domain entity.
        """
        self._data = entity_data
        self.recalculate()

    @abstractmethod
    def recalculate(self) -> None:
        """
        Recalculate geometry based on current entity data.

        Must be implemented by child classes to calculate bounding rect,
        shape, and visual properties.
        """
        pass

    @property
    def bounding_rect(self) -> QRectF:
        """Return the outer bounds of the item for collision/culling."""
        return self._bounding_rect

    @property
    def shape(self) -> QPainterPath:
        """Return the precise shape for drawing and collision detection."""
        return self._shape

    @property
    def color(self) -> QColor:
        """Return the fill color."""
        return self._color

    @property
    def border_color(self) -> QColor:
        """Return the border color."""
        return self._border_color