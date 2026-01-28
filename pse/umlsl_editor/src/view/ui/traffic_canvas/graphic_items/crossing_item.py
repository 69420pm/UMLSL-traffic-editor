# traffic_canvas/graphic_items/crossing_item.py

from typing import Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QPainter, QPen
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS


class CrossingItem(QGraphicsItem):
    """
    Graphics item representing the crossing area between one horizontal and one
    vertical road. It draws a background rectangle and a grid aligned to lane
    widths. The crossing Z-order reacts to the selection state of either road.

    road_1 and road_2 are expected to be graphics items exposing:
    - data(0).orientation, data(0).position, forward_lanes, backward_lanes
    - x(), y(), and an is_selected flag
    """

    def __init__(self, road_1: QGraphicsItem, road_2: QGraphicsItem):
        super().__init__()
        self._road_1 = road_1
        self._road_2 = road_2

        self._rect: QRectF = QRectF()
        self._grid_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)

        self._update_z_value()
        self.refresh_geometry()

    def _update_z_value(self) -> None:
        """Update Z-order based on selection state of connected roads."""
        is_selected = self._road_1.is_selected or self._road_2.is_selected
        z_value = Z_LAYERS.SELECTED_CROSSING if is_selected else Z_LAYERS.CROSSING
        self.setZValue(z_value)

    def _get_brush_color(self) -> QBrush:
        """Get the appropriate brush color based on selection state."""
        is_selected = self._road_1.is_selected or self._road_2.is_selected
        color = COLORS.LAYER.lighter() if is_selected else COLORS.LAYER
        return QBrush(color)

    def boundingRect(self) -> QRectF:
        return self._rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        # Update Z-value in case selection changed
        self._update_z_value()

        # Draw background rectangle
        painter.setBrush(self._get_brush_color())
        painter.setPen(Qt.NoPen)
        painter.drawRect(self._rect)

        # Draw grid
        painter.setPen(self._grid_pen)
        self._draw_grid(painter)

    def _draw_grid(self, painter: QPainter) -> None:
        """Draw the lane grid lines within the crossing area."""
        self._draw_vertical_grid_lines(painter)
        self._draw_horizontal_grid_lines(painter)

    def _draw_vertical_grid_lines(self, painter: QPainter) -> None:
        """Draw vertical grid lines spaced by lane width."""
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
        """Draw horizontal grid lines spaced by lane width."""
        lane_width = DIMENSION.LANE_WIDTH
        num_lines = int(self._rect.height() / lane_width) + 1

        for i in range(num_lines):
            y = self._rect.top() + i * lane_width
            if y <= self._rect.bottom():
                painter.drawLine(
                    QPointF(self._rect.left(), y),
                    QPointF(self._rect.right(), y),
                )

    def refresh_geometry(self) -> None:
        """Recalculate the intersection rectangle based on the two roads' positions and lane widths."""
        self.prepareGeometryChange()
        self._rect = self._calculate_intersection_rect()
        self.update()

    def _calculate_intersection_rect(self) -> QRectF:
        """Calculate the rectangle where the two roads intersect."""
        h_road, v_road = self._identify_road_orientations()

        x, width = self._calculate_vertical_road_bounds(v_road)
        y, height = self._calculate_horizontal_road_bounds(h_road)

        return QRectF(x, y, width, height)

    def _identify_road_orientations(self) -> tuple:
        """Identify which road is horizontal and which is vertical."""
        if self._road_1.data(0).orientation == RoadOrientation.HORIZONTAL:
            return self._road_1, self._road_2
        return self._road_2, self._road_1

    def _calculate_horizontal_road_bounds(self, h_road) -> tuple[float, float]:
        """Calculate the Y position and height for the horizontal road."""
        road_data = h_road.data(0)
        lane_width = DIMENSION.LANE_WIDTH

        forward_width = road_data.forward_lanes * lane_width
        total_width = (road_data.forward_lanes + road_data.backward_lanes) * lane_width

        y = (road_data.position - forward_width) + h_road.y()

        return y, total_width

    def _calculate_vertical_road_bounds(self, v_road) -> tuple[float, float]:
        """Calculate the X position and width for the vertical road."""
        road_data = v_road.data(0)
        lane_width = DIMENSION.LANE_WIDTH

        backward_width = road_data.backward_lanes * lane_width
        total_width = (road_data.forward_lanes + road_data.backward_lanes) * lane_width

        x = (road_data.position - backward_width) + v_road.x()

        return x, total_width
