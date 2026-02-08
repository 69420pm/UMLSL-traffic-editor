from typing import Optional

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, Qt
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import (
    SegmentInterval,
)
from pse.umlsl_editor.src.view.view_constants import Z_LAYERS


class SegmentIntervalItem(QGraphicsItem):
    """
    Graphics item that visualizes a segment interval on the traffic canvas.
    """

    def __init__(
            self,
            segment_interval: SegmentInterval,
            is_last_interval: bool,
            car: Car,
            application_controller: "ApplicationController",
    ) -> None:
        """
        Initialize the segment interval graphics item.

        Args:
            segment_interval: Domain interval to visualize.
            is_last_interval: Whether this interval is the final one in a chain.
            car: Car associated with this interval, used for visual properties like color.
            application_controller: Access to the snapshot reader for geometry.
        """
        super().__init__()

        self.segment_interval = segment_interval
        self.is_last_interval = is_last_interval
        self.color = car.color
        self.speed = car.speed
        self.application_controller = application_controller

        self._rect = QRectF()

        # Initial geometry calculation.
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
        Recalculate the interval rectangle based on the current snapshot geometry.
        """
        self.prepareGeometryChange()

        x_seg, y_seg = self.segment_interval.segment.get_position(
            self.application_controller.get_traffic_snapshot_reader())
        width_seg, height_seg = self.segment_interval.segment.get_size(
            self.application_controller.get_traffic_snapshot_reader())

        global_interval = self.segment_interval.get_global_interval(
            self.application_controller.get_traffic_snapshot_reader(), self.speed)

        is_horizontal = True

        if isinstance(self.segment_interval.segment, LaneSegment):
            road = self.application_controller.get_traffic_snapshot_reader().get_road_by_uid(
                self.segment_interval.segment.lane.road_uid)
            is_horizontal = road.orientation == RoadOrientation.HORIZONTAL

        if is_horizontal:
            x = x_seg + global_interval.start
            width = global_interval.length()
            y = y_seg
            height = height_seg

            # Horizontal lanes use a bottom-left origin in the frontend, so shift down by the interval height.
            y -= height
        else:
            x = x_seg
            width = width_seg
            y = y_seg - height_seg + global_interval.start
            height = global_interval.length()

        print(f"SegmentIntervalItem geometry: x={x}, y={y}, width={width}, height={height}")

        self._rect = QRectF(x, y, width, height)
        self.update()
