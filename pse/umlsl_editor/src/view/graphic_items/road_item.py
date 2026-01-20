# view/items/road_item.py
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush

from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation


class RoadItem(QGraphicsItem):
    """
    A single item that handles both the logic and rendering of a Road.
    Replaces RoadViewModel and RoadGraphicsItem.
    """

    def __init__(self, road: Road):
        super().__init__()
        self._road = road

        # Cache for geometry (recalculated only when data changes)
        self._bounding_rect = QRectF()
        self._center_line = QPainterPath()
        self._dashed_lines = QPainterPath()
        self._isSelected = False

        self.setFlag(QGraphicsItem.ItemIsMovable)

        # Setup static styles (or move to separate method if dynamic)
        self._setup_styles()

        # Initial calculation
        self._recalculate_geometry()


    def _setup_styles(self):
        # Z-Value management can be done here
        self.setZValue(Z_LAYERS.ROAD)


        self._asphalt_brush = QBrush(COLORS.RED if self._isSelected else COLORS.LAYER)

        self._center_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._center_pen.setCosmetic(False)  # Scale with zoom

        self._dashed_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._dashed_pen.setStyle(Qt.DashLine)
        self._dashed_pen.setDashPattern([4, 8])
        self._dashed_pen.setCosmetic(False)

    def boundingRect(self) -> QRectF:
        """
        Qt calls this to know how big the item is.
        Must be accurate or rendering artifacts occur.
        """
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        """
        The actual rendering loop.
        Draws the asphalt, then the center line, then dividers.
        """
        # 1. Draw Asphalt (Background)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._asphalt_brush)
        painter.drawRect(self._bounding_rect)

        # 2. Draw Center Line
        painter.setPen(self._center_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self._center_line)

        # 3. Draw Lane Dividers
        painter.setPen(self._dashed_pen)
        painter.drawPath(self._dashed_lines)

    def update_data(self, road: Road):
        """External hook to update the data and trigger a redraw."""
        self._road = road
        self.prepareGeometryChange()  # Critical: tells Qt bounds might change
        self._recalculate_geometry()
        self.update()  # Schedules a repaint

    def _recalculate_geometry(self) -> None:
        """Recalculate geometry and styles based on current road data."""
        road = self._road
        scene_size = DIMENSION.SCENE_SIZE
        lane_width = DIMENSION.LANE_WIDTH

        # Calculate asphalt rectangle
        width_f = road.forward_lanes * lane_width
        width_b = road.backward_lanes * lane_width

        if road.orientation == RoadOrientation.HORIZONTAL:
            y_start = road.position - width_f
            rect = QRectF(-scene_size / 2, y_start, scene_size, width_f + width_b)
        else:
            x_start = road.position - width_b
            rect = QRectF(x_start, -scene_size / 2, width_f + width_b, scene_size)

        self._bounding_rect = rect
        self._shape = QPainterPath()
        self._shape.addRect(rect)

        # Calculate center line (solid)
        self._calculate_center_line(road, scene_size)

        # Calculate lane dividers (dashed)
        self._calculate_lane_dividers(road, scene_size)


    def _calculate_center_line(self, road: Road, scene_size: int) -> None:
        """Calculate the center line path between traffic directions."""
        if road.forward_lanes >= 1 and road.backward_lanes >= 1:
            self._center_line = QPainterPath()
            if road.orientation == RoadOrientation.HORIZONTAL:
                self._center_line.moveTo(-scene_size / 2, road.position)
                self._center_line.lineTo(scene_size / 2, road.position)
            else:
                self._center_line.moveTo(road.position, -scene_size / 2)
                self._center_line.lineTo(road.position, scene_size / 2)

    def _calculate_lane_dividers(self, road: Road, scene_size: int) -> None:
        """Calculate the dashed lane divider paths."""
        self._dashed_lines = QPainterPath()
        lane_width = DIMENSION.LANE_WIDTH

        def add_divider(offset: float) -> None:
            if road.orientation == RoadOrientation.HORIZONTAL:
                self._dashed_lines.moveTo(-scene_size / 2, offset)
                self._dashed_lines.lineTo(scene_size / 2, offset)
            else:
                self._dashed_lines.moveTo(offset, -scene_size / 2)
                self._dashed_lines.lineTo(offset, scene_size / 2)

        for i in range(1, road.forward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                add_divider(road.position - (i * lane_width))
            else:
                add_divider(road.position + (i * lane_width))

        for i in range(1, road.backward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                add_divider(road.position + (i * lane_width))
            else:
                add_divider(road.position - (i * lane_width))

    def mousePressEvent(self, event):
        self._isSelected = not self._isSelected
        self._setup_styles()
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super().mousePressEvent(event)