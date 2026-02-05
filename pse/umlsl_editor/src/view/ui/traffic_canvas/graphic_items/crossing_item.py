"""
Crossing graphics item for the UMLSL Traffic Editor.

Provides a visual representation of the intersection area between two
perpendicular roads, including a background and lane grid.
"""

from typing import Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS


class CrossingItem(QGraphicsItem):
    """
    Graphics item representing the intersection of two perpendicular roads.

    Displays a rectangular crossing area with a lane grid overlay. The crossing
    automatically updates its position and appearance when either connected
    road is moved or selected.

    The crossing registers as a position listener on both roads so it can
    respond to road position changes.

    Attributes:
        road_1: The first connected road item.
        road_2: The second connected road item (perpendicular to road_1).
    """

    def __init__(self, road_1: RoadItem, road_2: RoadItem) -> None:
        """
        Initialize the crossing item between two roads.

        Args:
            road_1: The first road item (either horizontal or vertical).
            road_2: The second road item (must be perpendicular to road_1).
        """
        super().__init__()

        self.road_1 = road_1
        self.road_2 = road_2

        self._rect: QRectF = QRectF()

        self._grid_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_CROSSING_SEGMENT)
        self._grid_pen.setStyle(Qt.DashLine)
        pattern = [.05 / DIMENSION.LINE_WIDTH_CROSSING_SEGMENT, .1 / DIMENSION.LINE_WIDTH_CROSSING_SEGMENT]
        self._grid_pen.setDashPattern(pattern)
        self._update_z_value()
        self.refresh_geometry()

    # -------------------------------------------------------------------------
    # Visual State
    # -------------------------------------------------------------------------

    def _update_z_value(self) -> None:
        """Update the Z-order based on selection state of connected roads."""
        is_selected = self.road_1.is_selected or self.road_2.is_selected
        z_value = Z_LAYERS.SELECTED_CROSSING if is_selected else Z_LAYERS.CROSSING
        self.setZValue(z_value)

    def _get_brush_color(self) -> QBrush:
        """
        Get the brush color based on the selection state of connected roads.

        Returns:
            A QBrush with the appropriate fill color.
        """
        is_selected = self.road_1.is_selected or self.road_2.is_selected
        color = COLORS.LAYER.lighter() if is_selected else COLORS.LAYER
        return QBrush(color)

    # -------------------------------------------------------------------------
    # Graphics Interface
    # -------------------------------------------------------------------------

    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the crossing area."""
        return self._rect

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        """
        Paint the crossing area with background and grid.

        Args:
            painter: The QPainter to use for drawing.
            option: Style options for the item.
            widget: The widget being painted on.
        """
        self._update_z_value()

        painter.setBrush(self._get_brush_color())
        painter.setPen(Qt.NoPen)
        painter.drawRect(self._rect)

        painter.setPen(self._grid_pen)
        self._draw_grid(painter)

    def _draw_grid(self, painter: QPainter) -> None:
        """
        Draw the lane grid lines within the crossing area.

        Args:
            painter: The QPainter to use for drawing.
        """
        self._draw_vertical_grid_lines(painter)
        self._draw_horizontal_grid_lines(painter)

    def _draw_vertical_grid_lines(self, painter: QPainter) -> None:
        """
        Draw vertical grid lines spaced by lane width.

        Args:
            painter: The QPainter to use for drawing.
        """
        lane_width = DIMENSION.LANE_WIDTH
        num_lines = int(self._rect.width() / lane_width) + 1

        for i in range(num_lines):
            x = self._rect.left() + i * lane_width
            if x <= self._rect.right():
                painter.drawLine(
                    QPointF(x, self._rect.top()),
                    QPointF(x, self._rect.bottom()),
                )

    def _draw_horizontal_grid_lines(self, painter: QPainter) -> None:
        """
        Draw horizontal grid lines spaced by lane width.

        Args:
            painter: The QPainter to use for drawing.
        """
        lane_width = DIMENSION.LANE_WIDTH
        num_lines = int(self._rect.height() / lane_width) + 1

        for i in range(num_lines):
            y = self._rect.top() + i * lane_width
            if y <= self._rect.bottom():
                painter.drawLine(
                    QPointF(self._rect.left(), y),
                    QPointF(self._rect.right(), y),
                )

    # -------------------------------------------------------------------------
    # Geometry Calculation
    # -------------------------------------------------------------------------

    def refresh_geometry(self) -> None:
        """Recalculate the crossing rectangle based on current road positions."""
        self.prepareGeometryChange()
        self._rect = self._calculate_intersection_rect()
        self.update()

    def _calculate_intersection_rect(self) -> QRectF:
        """
        Calculate the rectangle where the two roads intersect.

        Returns:
            A QRectF defining the intersection area.
        """
        h_road, v_road = self._identify_road_orientations()

        x, width = self._calculate_vertical_road_bounds(v_road)
        y, height = self._calculate_horizontal_road_bounds(h_road)

        return QRectF(x, y, width, height)

    def _identify_road_orientations(self) -> tuple[RoadItem, RoadItem]:
        """
        Identify which road is horizontal and which is vertical.

        Returns:
            A tuple of (horizontal_road, vertical_road) items.
        """
        if self.road_1.data(0).orientation == RoadOrientation.HORIZONTAL:
            return self.road_1, self.road_2
        return self.road_2, self.road_1

    def _calculate_horizontal_road_bounds(
            self,
            h_road: RoadItem,
    ) -> tuple[float, float]:
        """
        Calculate the Y position and height for the horizontal road portion.

        Args:
            h_road: The horizontal road item.

        Returns:
            A tuple of (y_position, height) for the crossing rectangle.
        """
        road_data = h_road.data(0)
        lane_width = DIMENSION.LANE_WIDTH

        forward_width = road_data.number_of_forward_lanes * lane_width
        total_width = (
                              road_data.number_of_forward_lanes + road_data.number_of_backward_lanes
                      ) * lane_width

        y = (road_data.position - forward_width) + h_road.y()

        return y, total_width

    def _calculate_vertical_road_bounds(
            self,
            v_road: RoadItem,
    ) -> tuple[float, float]:
        """
        Calculate the X position and width for the vertical road portion.

        Args:
            v_road: The vertical road item.

        Returns:
            A tuple of (x_position, width) for the crossing rectangle.
        """
        road_data = v_road.data(0)
        lane_width = DIMENSION.LANE_WIDTH

        backward_width = road_data.number_of_backward_lanes * lane_width
        total_width = (
                              road_data.number_of_forward_lanes + road_data.number_of_backward_lanes
                      ) * lane_width

        x = (road_data.position - backward_width) + v_road.x()

        return x, total_width
