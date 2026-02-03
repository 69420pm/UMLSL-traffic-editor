from typing import Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPen, QColor
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION


class DebugSegmentItem(QGraphicsItem):
    def __init__(self, segment: Segment, application_controller: "ApplicationController"):
        super().__init__()
        self.segment = segment
        self.application_controller = application_controller

        self._rect: QRectF = QRectF()
        self._grid_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)

        self.setZValue(10000)
        self.refresh_geometry()

    def boundingRect(self) -> QRectF:
        return self._rect

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        painter.setBrush(QColor(0, 255, 0, 30))
        painter.setPen(QColor(0, 255, 0, 150))
        painter.drawRect(self._rect)

    def refresh_geometry(self) -> None:
        """Recalculate the intersection rectangle based on the two roads' positions and lane widths."""
        self.prepareGeometryChange()

        pos = self.segment.get_position(self.application_controller.get_traffic_snapshot_reader())
        size = self.segment.get_size(self.application_controller.get_traffic_snapshot_reader())

        self._rect = QRectF(pos[0], pos[1], size[0], size[1])
        self.update()
