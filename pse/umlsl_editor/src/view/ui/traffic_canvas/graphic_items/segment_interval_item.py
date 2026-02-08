from typing import Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter, Qt
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import SegmentInterval
from pse.umlsl_editor.src.view.view_constants import Z_LAYERS


class SegmentIntervalItem(QGraphicsItem):

    def __init__(self, segment_interval: SegmentInterval, is_last_interval: bool, color: QColor,
                 application_controller: "ApplicationController") -> None:
        """
        """
        super().__init__()

        self.segment_interval = segment_interval
        self.is_last_interval = is_last_interval
        self.color = color
        self.application_controller = application_controller

        self._rect = QRectF()

        # 2. Initial geometry calc
        self.refresh_geometry()

    # -------------------------------------------------------------------------
    # Visual State
    # -------------------------------------------------------------------------

    def _update_z_value(self) -> None:
        """Update the Z-order based on selection state of connected roads."""
        self.setZValue(Z_LAYERS.SEGMENT_INTERVAL)

    # -------------------------------------------------------------------------
    # Graphics Interface (Qt)
    # -------------------------------------------------------------------------

    def boundingRect(self) -> QRectF:
        return self._rect

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        self._update_z_value()

        # Background
        painter.setBrush(self.color)
        painter.setPen(Qt.NoPen)

        painter.drawRect(self._rect)

    def refresh_geometry(self):
        """
        Recalculate the crossing rectangle based on current road positions.
        Called by RoadItem via the GeometryListener protocol.
        """
        self.prepareGeometryChange()

        x_seg, y_seg = self.segment_interval.segment.get_position(
            self.application_controller.get_traffic_snapshot_reader())
        width_seg, height_seg = self.segment_interval.segment.get_size(
            self.application_controller.get_traffic_snapshot_reader())

        is_horizontal = True

        if is_horizontal:
            x = x_seg + self.segment_interval.interval.start
            width = self.segment_interval.interval.end - self.segment_interval.interval.start
            y = y_seg
            height = height_seg

            y -= height
        else:
            x = x_seg
            width = width_seg
            y = y_seg + self.segment_interval.interval.start
            height = self.segment_interval.interval.end - self.segment_interval.interval.start

            x -= width

        self._rect = QRectF(x, y, width, height)
        self.update()
