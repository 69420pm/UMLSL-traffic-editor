"""
Debug segment item for the UMLSL Traffic Editor.

Provides a visual representation of segment boundaries for debugging purposes.
Segments are displayed as semi-transparent rectangles overlaid on the traffic scene.
"""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController


class DebugSegmentItem(QGraphicsItem):
    """
    Graphics item for visualizing segment boundaries during debugging.

    Displays a segment as a semi-transparent green rectangle with a visible
    border. This is useful for verifying segment positions and sizes in the
    traffic model.

    Attributes:
        segment: The segment entity being visualized.
        application_controller: Reference to the application controller.
    """

    # Visual style constants
    FILL_COLOR = QColor(0, 255, 0, 30)
    BORDER_COLOR = QColor(0, 255, 0, 150)
    Z_VALUE = 10000

    def __init__(
            self,
            segment: Segment,
            application_controller: "ApplicationController",
    ) -> None:
        """
        Initialize the debug segment item.

        Args:
            segment: The segment entity to visualize.
            application_controller: The application controller for accessing
                the traffic snapshot reader.
        """
        super().__init__()

        self._segment = segment
        self._application_controller = application_controller
        self._rect = QRectF()
        self._border_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)

        self.setZValue(self.Z_VALUE)
        self.refresh_geometry()

    @property
    def segment(self) -> Segment:
        """Get the segment entity being visualized."""
        return self._segment

    def boundingRect(self) -> QRectF:
        """
        Return the bounding rectangle of the segment.

        Returns:
            The rectangle defining the segment's bounds.
        """
        return self._rect

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        """
        Paint the debug segment as a semi-transparent rectangle.

        Args:
            painter: The QPainter to use for drawing.
            option: Style options for the item (unused).
            widget: The widget being painted on (unused).
        """
        painter.setBrush(self.FILL_COLOR)
        painter.setPen(QPen(self.BORDER_COLOR, DIMENSION.LINE_WIDTH_ROAD_DIVIDER))
        painter.drawRect(self._rect)

    def refresh_geometry(self) -> None:
        """
        Recalculate the segment rectangle based on current model state.

        Queries the traffic snapshot reader for the segment's current
        position and size, then updates the display rectangle.
        """
        self.prepareGeometryChange()

        snapshot_reader = self._application_controller.get_traffic_snapshot_reader()
        position = self._segment.get_position(snapshot_reader)
        size = self._segment.get_size(snapshot_reader)

        self._rect = QRectF(position[0], position[1] - size[1], size[0], size[1])
        self.update()
