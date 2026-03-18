import logging
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsScene, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.errors.car_errors import (
    CarTrafficSnapshotContextValidationError,
    CarValidationError,
)
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.segment_interval_item import (
    SegmentIntervalItem,
)
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import (
    SelectableGraphicsItem,
)
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

logger = logging.getLogger(__name__)


class CarItemStyle:
    PEN_WIDTH = 0.07
    HOVER_LIGHTNESS = 110
    LABEL_SCALE_THRESHOLD = DIMENSION.GRID_FINE_THRESHOLD


class CarItem(SelectableGraphicsItem):
    def __init__(
            self,
            car: Car,
            road_item: RoadItem,
            application_controller: "ApplicationController",
    ) -> None:
        super().__init__(application_controller)

        self._car = car
        self._road_item = road_item
        self._road = road_item.data(0)

        self._segments = []

        self._polygon = QPolygonF()
        self._body_brush = QBrush()
        self._body_pen = QPen()

        self._road_item.add_position_listener(self)
        self.update_data(car)

    def cleanup(self) -> None:
        if self._road_item:
            self._road_item.remove_position_listener(self)
        self._clear_segments()

    def update_data(self, car: Car, road_item: Optional[RoadItem] = None) -> None:
        self._car = car
        self.setData(0, car)

        if road_item is not None and road_item != self._road_item:
            self._road_item.remove_position_listener(self)
            self._road_item = road_item
            self._road = road_item.data(0)
            self._road_item.add_position_listener(self)

        if self._road_item:
            self._road = self._road_item.data(0)

        self.refresh_geometry()

    def update_segments(self) -> None:
        self._clear_segments()

        if self.is_selected:
            self._add_segments(
                self._car.environment.path_segment_intervals,
                self._car,
                False
            )

        self._add_segments(
            self._car.environment.reserved,
            self._car,
            False
        )
        self._add_segments(
            self._car.environment.claimed,
            self._car,
            True
        )

    def _clear_segments(self) -> None:
        scene = self._get_scene()
        if scene is None:
            self._segments.clear()
            return
        for seg in self._segments:
            scene.removeItem(seg)
        self._segments.clear()

    def _add_segments(self, segments, car: Car, should_ignore_lane_direction: bool) -> None:
        scene = self._get_scene()
        if scene is None:
            return
        for seg_data in segments:
            seg_item = SegmentIntervalItem(
                segment_interval=seg_data,
                application_controller=self.application_controller,
                car=self._car,
                is_last_interval=False,
                should_ignore_lane_direction=should_ignore_lane_direction,
            )
            scene.addItem(seg_item)
            self._segments.append(seg_item)

    def _get_scene(self) -> QGraphicsScene | None:
        return self.scene()

    def _get_constraint_for_orientation(self, orientation: RoadOrientation) -> int:
        if orientation == RoadOrientation.HORIZONTAL:
            return SelectableGraphicsItem.AXIS_X_ONLY
        return SelectableGraphicsItem.AXIS_Y_ONLY

    def _update_styles(self) -> None:
        self.setZValue(Z_LAYERS.SELECTED_CAR if self.is_selected else Z_LAYERS.CAR)

        constraint = self._get_constraint_for_orientation(self._road.orientation)
        self.set_movement_constraint(constraint)

        car_color = QColor(self._car.color)
        if self.is_hovered:
            car_color = car_color.lighter(CarItemStyle.HOVER_LIGHTNESS)

        border_color = COLORS.TEXT if self.is_selected else COLORS.TRANSPARENT
        self._body_brush = QBrush(car_color)
        self._body_pen = QPen(border_color, CarItemStyle.PEN_WIDTH)

    def on_selection_changed(self, is_selected: bool) -> None:
        self._update_styles()
        self.update_segments()
        self.update()

    def on_hover_changed(self, is_hovered: bool) -> None:
        self._update_styles()
        self.update()

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        is_horiz = self._road.orientation == RoadOrientation.HORIZONTAL
        delta = delta_x if is_horiz else delta_y
        new_position = self._car.position_on_lane + delta

        try:
            self.application_controller.command_controller.edit_car(
                car=self._car,
                position_on_lane=new_position,
            )
        except (CarValidationError, CarTrafficSnapshotContextValidationError) as e:
            view = self.scene().views()[0] if self.scene().views() else None
            WarningDialog("Cannot move car", str(e), view).exec()

    def boundingRect(self) -> QRectF:
        return self._polygon.boundingRect()

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        painter.setPen(self._body_pen)
        painter.setBrush(self._body_brush)
        painter.drawPolygon(self._polygon)
        self._paint_label(painter, option)

    def _paint_label(self, painter: QPainter, option: QStyleOptionGraphicsItem) -> None:
        transform = painter.worldTransform()
        lod = option.levelOfDetailFromTransform(transform)

        if lod <= CarItemStyle.LABEL_SCALE_THRESHOLD:
            return

        text_scale = 1.0 / lod
        painter.save()

        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(COLORS.BACKGROUND)

        center = self._polygon.boundingRect().center()
        painter.translate(center.x(), center.y())
        painter.scale(text_scale, -text_scale)

        text = str(self._car.name)
        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(text)

        painter.drawText(
            -text_rect.width() / 2,
            text_rect.height() / 4,
            text
        )
        painter.restore()

    def refresh_geometry(self) -> None:
        """
        Recalculates polygon.
        Anchor: car.position_on_lane corresponds to the BACK of the car.
        """
        self._update_styles()
        self.prepareGeometryChange()

        car = self._car
        road = self._road
        lane_idx = car.lane.lane_index
        is_vertical = road.orientation == RoadOrientation.VERTICAL
        is_backward = (lane_idx < 0) != (car.speed < 0)

        # Define the local car shape with the rear anchored at (0, 0).
        # The polygon is defined facing positive X; direction is adjusted later.
        l, w, t = car.length, DIMENSION.CAR_WIDTH / 2.0, DIMENSION.CAR_TRIANGLE_LENGTH

        points = [
            QPointF(0, -w),  # Back-Right
            QPointF(l - t, -w),  # Shoulder-Right
            QPointF(l, 0),  # Tip
            QPointF(l - t, w),  # Shoulder-Left
            QPointF(0, w)  # Back-Left
        ]

        # Calculate world-space offsets for lane center and transition.
        lane_w = DIMENSION.LANE_WIDTH

        # Determine lateral direction/offset logic
        vert_mod = 1 if is_vertical else -1
        dir_mod = -1 if is_backward else 1

        center_offset = (lane_idx * lane_w * vert_mod) + \
                        (lane_w / 2.0 * vert_mod) \
 \
        # If the car has claimed lanes, apply the transition offset to shift towards the claimed lane.
        if len(car.environment.claimed_lanes) > 0:
            center_offset += (car.transition * lane_w * dir_mod * vert_mod)

        road_base = road.position + (self._road_item.x() if is_vertical else self._road_item.y())
        lat_pos = road_base + center_offset
        long_pos = car.position_on_lane

        # Transform local points into world coordinates.
        poly_points = []
        for p in points:
            # If backward lane, flip longitudinal direction (face negative)
            lx = -p.x() if is_backward else p.x()
            ly = p.y()

            if is_vertical:
                # Vertical: Long=Y, Lat=X
                poly_points.append(QPointF(lat_pos + ly, long_pos + lx))
            else:
                # Horizontal: Long=X, Lat=Y
                poly_points.append(QPointF(long_pos + lx, lat_pos + ly))

        self._polygon = QPolygonF(poly_points)
        self.update()
