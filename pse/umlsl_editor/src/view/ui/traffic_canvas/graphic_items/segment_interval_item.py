from typing import Optional

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF, Qt
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import (
    CrossingSegment,
)
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import (
    LaneSegment,
)
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment_interval import (
    SegmentInterval,
    ViewSegmentIntervall,
)
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS


class SegmentIntervalItem(QGraphicsItem):
    """Base graphics item for segment intervals."""

    def __init__(
            self,
            segment_interval: SegmentInterval,
            lane_start: "Lane",
            lane_end: "Lane",
            is_last_interval: bool,
            car: Car,
            application_controller: "ApplicationController",
    ) -> None:
        super().__init__()
        self.segment_interval = segment_interval
        self.is_last_interval = is_last_interval
        self.car = car
        self.application_controller = application_controller
        self.lane_start = lane_start
        self.lane_end = lane_end

        self.color = QColor(car.color)
        self.color.setAlphaF(0.5)
        self.brush = QBrush(self.color)
        self.pen = Qt.NoPen

        self._rect = QRectF()

        self._setup_style()
        self.refresh_geometry()

    @property
    def should_ignore_lane_direction(self) -> bool:
        return False

    @property
    def should_extend_car(self) -> bool:
        return False

    def _setup_style(self) -> None:
        """Hook for subclasses to override visual styles."""
        pass

    def _update_z_value(self) -> None:
        self.setZValue(Z_LAYERS.SEGMENT_INTERVAL)

    def boundingRect(self) -> QRectF:
        return self._rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None) -> None:
        self._update_z_value()
        painter.setBrush(self.brush)
        painter.setPen(self.pen)

        if hasattr(self, '_path') and not self._path.isEmpty():
            painter.drawPath(self._path)
        else:
            painter.drawRect(self._rect)

    def refresh_geometry(self) -> None:
        self.prepareGeometryChange()

        reader = self.application_controller.get_traffic_snapshot_reader()
        x_seg, y_seg = self.segment_interval.segment.get_position(reader)
        width_seg, height_seg = self.segment_interval.segment.get_size(reader)

        global_interval = self.segment_interval.get_global_interval(
            reader, self.car, self.should_ignore_lane_direction
        )

        is_horizontal = True
        is_corner = False

        if isinstance(self.segment_interval.segment, LaneSegment):
            road = reader.get_road_by_uid(self.segment_interval.segment.lane.road_uid)
            is_horizontal = road.orientation == RoadOrientation.HORIZONTAL

        if isinstance(self.segment_interval.segment, CrossingSegment):
            crossing_segment = self.segment_interval.segment
            horizontal_lane = crossing_segment.horizontal_lane
            vertical_lane = crossing_segment.vertical_lane
            if (
                (horizontal_lane == self.lane_start and vertical_lane == self.lane_end)
                or (horizontal_lane == self.lane_end and vertical_lane == self.lane_start)
            ):
                is_corner = True
            else:
                is_horizontal = horizontal_lane in (self.lane_start, self.lane_end)

        self._path = QPainterPath()
        self._path.setFillRule(Qt.WindingFill)

        if is_corner:
            # Corner calculations dynamically merge the horizontal and vertical rects
            # while carving out the interior to render corner transitions properly
            hx, hy = x_seg, y_seg - height_seg
            hw, hh = width_seg, height_seg
            if self.should_extend_car:
                hy += (DIMENSION.LANE_WIDTH - DIMENSION.CAR_WIDTH) / 2
                hh = DIMENSION.CAR_WIDTH

            vx, vy = x_seg, y_seg - height_seg
            vw, vh = width_seg, height_seg
            if self.should_extend_car:
                vx += (DIMENSION.LANE_WIDTH - DIMENSION.CAR_WIDTH) / 2
                vw = DIMENSION.CAR_WIDTH

            ox = max(hx, vx)
            oy = max(hy, vy)
            ow = min(hx + hw, vx + vw) - ox
            oh = min(hy + hh, vy + vh) - oy

            final_hx, final_hy, final_hw, final_hh = hx, hy, hw, hh
            final_vx, final_vy, final_vw, final_vh = vx, vy, vw, vh

            horizontal_is_entry = (self.lane_start == horizontal_lane)
            if self.lane_start != horizontal_lane and self.lane_start != vertical_lane:
                horizontal_is_entry = (self.car.lane.road.orientation == RoadOrientation.HORIZONTAL)

            is_reverse = self.car.speed < 0
            h_moves_right = (horizontal_lane.lane_index >= 0) != is_reverse
            v_moves_down = (vertical_lane.lane_index >= 0) != is_reverse

            if horizontal_is_entry:
                keep_left_arm = h_moves_right
                keep_top_arm = not v_moves_down
            else:
                keep_left_arm = not h_moves_right
                keep_top_arm = v_moves_down

            if keep_left_arm:
                final_hw = (ox + ow) - hx
            else:
                final_hx = ox
                final_hw = (hx + hw) - ox

            if keep_top_arm:
                final_vh = (oy + oh) - vy
            else:
                final_vy = oy
                final_vh = (vy + vh) - oy

            self._path.addRect(QRectF(final_hx, final_hy, final_hw, final_hh))
            self._path.addRect(QRectF(final_vx, final_vy, final_vw, final_vh))
            self._rect = self._path.boundingRect()

        else:
            # Base Interval positioning mapping
            if is_horizontal:
                x = x_seg + global_interval.start
                width = global_interval.length()
                y = y_seg - height_seg
                height = height_seg
                if self.should_extend_car:
                    height = DIMENSION.CAR_WIDTH
                    y += (DIMENSION.LANE_WIDTH - DIMENSION.CAR_WIDTH) / 2
            else:
                x = x_seg
                width = width_seg
                y = y_seg - height_seg + global_interval.start
                height = global_interval.length()
                if self.should_extend_car:
                    width = DIMENSION.CAR_WIDTH
                    x += (DIMENSION.LANE_WIDTH - DIMENSION.CAR_WIDTH) / 2

            if self.is_last_interval and self.should_extend_car:
                lane_idx = self.lane_end.lane_index
                is_backward = (lane_idx < 0) != (self.car.speed < 0)

                # We carve the tip OUT of the interval width/height.
                # The total span strictly remains within [x, x+width] or [y, y+height].
                t = DIMENSION.CAR_TRIANGLE_LENGTH

                if is_horizontal:
                    if not is_backward:
                        # Moving Right (->)
                        # Flat corners are pushed back by `t`. The tip extends exactly to `x + width`.
                        poly = QPolygonF([
                            QPointF(x, y),  # Top-left
                            QPointF(x + width - t, y),  # Top-right (carved)
                            QPointF(x + width, y + height / 2.0),  # Tip point (max bounds)
                            QPointF(x + width - t, y + height),  # Bottom-right (carved)
                            QPointF(x, y + height)  # Bottom-left
                        ])
                    else:
                        # Moving Left (<-)
                        # Flat corners start at `x + t`. The tip extends exactly to `x`.
                        poly = QPolygonF([
                            QPointF(x + width, y),  # Top-right
                            QPointF(x + width, y + height),  # Bottom-right
                            QPointF(x + t, y + height),  # Bottom-left (carved)
                            QPointF(x, y + height / 2.0),  # Tip point (min bounds)
                            QPointF(x + t, y)  # Top-left (carved)
                        ])
                    self._path.addPolygon(poly)
                else:
                    if not is_backward:
                        # Moving Down (v)
                        # Flat corners pushed up by `t`. The tip extends exactly to `y + height`.
                        poly = QPolygonF([
                            QPointF(x, y),  # Top-left
                            QPointF(x + width, y),  # Top-right
                            QPointF(x + width, y + height - t),  # Bottom-right (carved)
                            QPointF(x + width / 2.0, y + height),  # Tip point (max bounds)
                            QPointF(x, y + height - t)  # Bottom-left (carved)
                        ])
                    else:
                        # Moving Up (^)
                        # Flat corners start at `y + t`. The tip extends exactly to `y`.
                        poly = QPolygonF([
                            QPointF(x, y + height),  # Bottom-left
                            QPointF(x + width, y + height),  # Bottom-right
                            QPointF(x + width, y + t),  # Top-right (carved)
                            QPointF(x + width / 2.0, y),  # Tip point (min bounds)
                            QPointF(x, y + t)  # Top-left (carved)
                        ])
                    self._path.addPolygon(poly)

                self._rect = self._path.boundingRect()
            else:
                self._rect = QRectF(x, y, width, height)

        self.update()


class PathSegmentItem(SegmentIntervalItem):
    """Visualizes standard path segments."""

    def _setup_style(self) -> None:
        self.pen = QPen(COLORS.TEXT, .04)
        self.pen.setCosmetic(False)
        self.color = QColor(COLORS.TEXT)
        self.color.setAlphaF(0.2)
        self.brush.setColor(self.color)


class ViewSegmentItem(SegmentIntervalItem):
    """Visualizes view lanes with a soft background fill."""

    def _setup_style(self) -> None:
        self.pen = Qt.NoPen
        self.color = QColor(175, 195, 215)
        self.color.setAlphaF(0.25)
        self.brush.setColor(self.color)


class ReservedSegmentItem(SegmentIntervalItem):
    """Visualizes reserved segments, adjusting for car width."""

    @property
    def should_extend_car(self) -> bool:
        return True


class ClaimedSegmentItem(SegmentIntervalItem):
    """Visualizes claimed segments using a dashed outline."""

    @property
    def should_ignore_lane_direction(self) -> bool:
        return True

    def _setup_style(self) -> None:
        self.pen = QPen(COLORS.TEXT, .04)
        self.pen.setStyle(Qt.DashLine)
        self.pen.setDashPattern([2, 2])
        self.pen.setCosmetic(False)
        self.color = QColor(COLORS.TEXT)
        self.color.setAlphaF(0.4)
        self.brush.setColor(self.color)
