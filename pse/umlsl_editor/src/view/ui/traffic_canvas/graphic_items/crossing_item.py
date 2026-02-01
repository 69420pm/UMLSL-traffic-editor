# traffic_canvas/graphic_items/crossing_item.py

from PySide6.QtCore import QRectF, Qt, QPointF  # Added QPointF
from PySide6.QtGui import QBrush, QPen
from PySide6.QtWidgets import QGraphicsItem

from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.view.view_constants import DIMENSION, Z_LAYERS, COLORS


class CrossingItem(QGraphicsItem):
    """
    Visual representation of a crossing between a horizontal and a vertical road.
    """

    def __init__(self, road_1, road_2):
        super().__init__()
        self.road_1 = road_1
        self.road_2 = road_2

        # Ensure we are drawn above the roads
        self.setZValue(Z_LAYERS.CROSSING)

        self._rect = QRectF()
        self.refresh_geometry()

    def boundingRect(self) -> QRectF:
        return self._rect

    def paint(self, painter, option, widget=None):
        # 1. Draw the Background Rectangle
        on_road_is_selected = self.road_1.is_selected or self.road_2.is_selected
        self.setZValue(Z_LAYERS.SELECTED_CROSSING if on_road_is_selected else Z_LAYERS.CROSSING)

        color = COLORS.LAYER.lighter() if on_road_is_selected else COLORS.LAYER
        painter.setBrush(QBrush(color))

        # No border for the rect itself, the grid will define the structure
        painter.setPen(Qt.NoPen)
        painter.drawRect(self._rect)

        # 2. Configure Pen for the Grid (Dashed)
        grid_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        # grid_pen.setStyle(Qt.DashLine)
        # grid_pen.setDashPattern([4, 8])  # Matches standard road dash pattern
        painter.setPen(grid_pen)

        # vertical lines
        x = self._rect.topLeft().x()
        while x <= self._rect.topRight().x():
            painter.drawLine(
                QPointF(x, self._rect.top()),
                QPointF(x, self._rect.bottom())
            )
            x += DIMENSION.LANE_WIDTH

        # horizontal lines
        y = self._rect.topLeft().y()
        while y <= self._rect.bottomLeft().y():
            painter.drawLine(
                QPointF(self._rect.left(), y),
                QPointF(self._rect.right(), y)
            )
            y += DIMENSION.LANE_WIDTH

    def refresh_geometry(self):
        """Recalculates the intersection rectangle based on road positions."""
        self.prepareGeometryChange()

        # Identify which road is horizontal and which is vertical
        if self.road_1.data(0).orientation == RoadOrientation.HORIZONTAL:
            h_road, v_road = self.road_1, self.road_2
        else:
            h_road, v_road = self.road_2, self.road_1

        # 1. Calculate Horizontal Road Geometry (Y-axis position & Height)
        h_width_f = h_road.data(0).number_of_forward_lanes * DIMENSION.LANE_WIDTH
        h_width_total = (h_road.data(0).number_of_forward_lanes + h_road.data(
            0).number_of_backward_lanes) * DIMENSION.LANE_WIDTH

        h_y = (h_road.data(0).position - h_width_f) + h_road.y()

        # 2. Calculate Vertical Road Geometry (X-axis position & Width)
        v_width_b = v_road.data(0).number_of_backward_lanes * DIMENSION.LANE_WIDTH
        v_width_total = (v_road.data(0).number_of_forward_lanes + v_road.data(
            0).number_of_backward_lanes) * DIMENSION.LANE_WIDTH

        v_x = (v_road.data(0).position - v_width_b) + v_road.x()

        # 3. Create the intersection rectangle
        self._rect = QRectF(v_x, h_y, v_width_total, h_width_total)
        self.update()
