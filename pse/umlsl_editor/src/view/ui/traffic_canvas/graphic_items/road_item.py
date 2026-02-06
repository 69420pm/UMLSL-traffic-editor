"""
Road graphics item for the UMLSL Traffic Editor.

Provides a visual representation of a road on the traffic canvas, including
lane dividers, center lines, and sticky labels that remain visible at
viewport edges.
"""

import logging
from typing import TYPE_CHECKING, List, Optional, Protocol, runtime_checkable

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QPainter, QPainterPath, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

# Resource import (prevent unused import linters from removing it)
import pse.umlsl_editor.src.view.widgets.qt_widgets.resources_rc as rc  # noqa: F401
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.model.errors.road_errors import RoadValidationError, RoadTrafficSnapshotContextValidationError
from pse.umlsl_editor.src.view.ui.exeption_handling.warning_dialog import WarningDialog
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import (
    SelectableGraphicsItem,
)
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

logger = logging.getLogger(__name__)


@runtime_checkable
class GeometryListener(Protocol):
    """Protocol for objects that listen to geometry changes."""

    def refresh_geometry(self) -> None: ...


class RoadItemStyle:
    """Constants and styling configuration for the RoadItem."""
    ARROW_SVG_PATH = ":/icons/arrow_downward.svg"
    ARROW_BASE_SIZE = 16.0
    LABEL_ARROW_SPACING = 18.0

    # Text and Layout
    TEXT_PADDING = 10.0
    NAME_V_OFFSET = 8.0
    NAME_H_OFFSET = 16.0

    # Line Styling
    DASH_PATTERN = [4, 8]


class RoadItem(SelectableGraphicsItem):
    """
    Graphics item representing a road with multiple lanes.

    Displays a road spanning the scene with:
        - Asphalt background colored by selection/hover state
        - Solid center line separating forward and backward lanes
        - Dashed lane dividers between lanes in the same direction
        - Sticky labels that remain visible at viewport edges
    """

    def __init__(
            self,
            road: Road,
            application_controller: "ApplicationController",
    ) -> None:
        super().__init__(application_controller)

        self._road = road
        self._position_listeners: List[GeometryListener] = []

        # Graphics Cache
        self._bounding_rect = QRectF()
        self._center_line = QPainterPath()
        self._dashed_lines = QPainterPath()
        self._asphalt_brush = QBrush()
        self._center_pen = QPen()
        self._dashed_pen = QPen()

        self._arrow_renderer = QSvgRenderer(RoadItemStyle.ARROW_SVG_PATH)
        if not self._arrow_renderer.isValid():
            logger.warning("Failed to load SVG: %s", RoadItemStyle.ARROW_SVG_PATH)

        self.update_data(road)

    def update_data(self, road: Road) -> None:
        """Update the road's display data and refresh geometry."""
        self._road = road
        self.setData(0, road)

        # Ensure selection state is valid if orientation changed
        super().check_current_selection()

        constraint = self._get_constraint_for_orientation(road.orientation)
        self.set_movement_constraint(constraint)

        self._update_styles()
        self.prepareGeometryChange()
        self._recalculate_geometry()
        self.update()

        self._notify_listeners()

    # -------------------------------------------------------------------------
    # Movement Constraints
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_constraint_for_orientation(orientation: RoadOrientation) -> int:
        """Return the movement axis constraint based on road orientation."""
        if orientation == RoadOrientation.HORIZONTAL:
            return SelectableGraphicsItem.AXIS_Y_ONLY
        return SelectableGraphicsItem.AXIS_X_ONLY

    # -------------------------------------------------------------------------
    # Visual Styling
    # -------------------------------------------------------------------------

    def _update_styles(self) -> None:
        """Update pens and brushes based on selection and hover state."""
        # Z-Index
        self.setZValue(Z_LAYERS.SELECTED_ROAD if self.is_selected else Z_LAYERS.ROAD)

        # Background Color
        color = COLORS.LAYER.lighter() if self.is_selected else COLORS.LAYER
        if self.is_hovered:
            color = color.lighter(110)
        self._asphalt_brush = QBrush(color)

        # Pens
        self._center_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._center_pen.setCosmetic(False)

        self._dashed_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._dashed_pen.setStyle(Qt.DashLine)
        self._dashed_pen.setDashPattern(RoadItemStyle.DASH_PATTERN)
        self._dashed_pen.setCosmetic(False)

    # -------------------------------------------------------------------------
    # SelectableGraphicsItem Lifecycle Hooks
    # -------------------------------------------------------------------------

    def on_selection_changed(self, is_selected: bool) -> None:
        self._update_styles()

    def on_hover_changed(self, is_hovered: bool) -> None:
        self._update_styles()

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        """Calculate new position after drag and issue command."""
        if self._road.orientation == RoadOrientation.HORIZONTAL:
            new_position = self._road.position + delta_y
        else:
            new_position = self._road.position + delta_x

        try:
            self.application_controller.command_controller.update_road(
                road=self._road,
                position=new_position,
            )
        except (RoadValidationError, RoadTrafficSnapshotContextValidationError) as e:
            view = self.scene().views()[0] if self.scene().views() else None

            dialog = WarningDialog(
                "Cannot Move Road",
                str(e),
                view,
            )
            dialog.exec()

    # -------------------------------------------------------------------------
    # Position Listeners (Observer Pattern)
    # -------------------------------------------------------------------------

    def add_position_listener(self, listener: GeometryListener) -> None:
        """Register an object to be notified when this road moves."""
        if listener not in self._position_listeners:
            self._position_listeners.append(listener)

    def remove_position_listener(self, listener: GeometryListener) -> None:
        if listener in self._position_listeners:
            self._position_listeners.remove(listener)

    def _notify_listeners(self) -> None:
        for listener in self._position_listeners:
            listener.refresh_geometry()

    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: any) -> any:
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._notify_listeners()
        return super().itemChange(change, value)

    # -------------------------------------------------------------------------
    # Graphics Interface (Qt)
    # -------------------------------------------------------------------------

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        # 1. Background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._asphalt_brush)
        painter.drawRect(self._bounding_rect)

        # 2. Lines
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._center_pen)
        painter.drawPath(self._center_line)

        painter.setPen(self._dashed_pen)
        painter.drawPath(self._dashed_lines)

        # 3. Sticky Labels
        self._paint_sticky_elements(painter, option)

    # -------------------------------------------------------------------------
    # Label & Arrow Painting
    # -------------------------------------------------------------------------

    def _paint_sticky_elements(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
    ) -> None:
        """Draw labels and arrows that stick to the viewport edges."""
        transform = painter.worldTransform()

        # Calculate viewport top-left in scene coordinates
        inv_transform, invertible = transform.inverted()
        if not invertible:
            return

        lod = option.levelOfDetailFromTransform(transform)
        text_scale = 1.0 / lod

        screen_top_left = inv_transform.map(QPointF(0, 0))
        padding = RoadItemStyle.TEXT_PADDING * text_scale

        view_bounds = QPointF(
            screen_top_left.x() + padding,
            screen_top_left.y() - padding
        )

        painter.save()
        painter.setPen(COLORS.TEXT)

        self._paint_road_name(painter, text_scale, view_bounds)

        if lod > DIMENSION.GRID_FINE_THRESHOLD:
            self._paint_lane_details(painter, text_scale, view_bounds)

        painter.restore()

    def _paint_road_name(
            self,
            painter: QPainter,
            scale: float,
            view_bounds: QPointF
    ) -> None:
        """Draws the main road name."""
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        lane_width = DIMENSION.LANE_WIDTH
        road = self._road
        is_horizontal = road.orientation == RoadOrientation.HORIZONTAL

        v_offset = RoadItemStyle.NAME_V_OFFSET * scale
        h_offset = RoadItemStyle.NAME_H_OFFSET * scale

        if is_horizontal:
            y_pos = road.position + v_offset + (road.number_of_backward_lanes * lane_width)
            self._draw_text(painter, road.name, view_bounds.x(), y_pos, scale)
        else:
            x_pos = road.position - (road.number_of_backward_lanes * lane_width) - h_offset
            self._draw_text(painter, road.name, x_pos, view_bounds.y(), scale)

    def _paint_lane_details(
            self,
            painter: QPainter,
            scale: float,
            view_bounds: QPointF
    ) -> None:
        """Iterates over lanes to draw IDs and direction arrows."""
        font = painter.font()
        font.setBold(False)
        painter.setFont(font)

        road = self._road
        lane_width = DIMENSION.LANE_WIDTH
        arrow_dist = RoadItemStyle.LABEL_ARROW_SPACING * scale
        is_horizontal = road.orientation == RoadOrientation.HORIZONTAL

        def draw_lane_set(count: int, prefix: str, is_forward: bool):
            for i in range(count):
                offset = (i + 0.5) * lane_width

                # Determine perpendicular offset based on direction
                if is_forward:
                    # Standard implementation for forward usually implies specific side
                    # Assuming standard RHT: Forward is usually Right/Bottom depending on axis system,
                    # but here we follow the original logic's offset math.
                    pos_perp = (road.position - offset) if is_horizontal else (road.position + offset)
                else:
                    pos_perp = (road.position + offset) if is_horizontal else (road.position - offset)

                # Calculate specific X/Y
                if is_horizontal:
                    text_pt = QPointF(view_bounds.x(), pos_perp)
                    arrow_pt = QPointF(view_bounds.x() + arrow_dist, pos_perp)
                else:
                    text_pt = QPointF(pos_perp, view_bounds.y())
                    arrow_pt = QPointF(pos_perp, view_bounds.y() - arrow_dist)

                # Draw
                self._draw_text(painter, f"{prefix}{i + 1}", text_pt.x(), text_pt.y(), scale)
                self._draw_arrow(painter, arrow_pt, scale, is_forward, is_horizontal)

        draw_lane_set(road.number_of_forward_lanes, "f", is_forward=True)
        draw_lane_set(road.number_of_backward_lanes, "b", is_forward=False)

    def _draw_text(
            self,
            painter: QPainter,
            text: str,
            x: float,
            y: float,
            scale: float
    ) -> None:
        """Helper to draw text that resists viewport scaling."""
        painter.save()
        painter.translate(x, y)
        painter.scale(scale, -scale)  # Flip Y for text rendering

        fm = painter.fontMetrics()
        rect = fm.boundingRect(text)

        # Center horizontally, offset vertically slightly
        painter.drawText(-rect.width() / 2, rect.height() / 4, text)
        painter.restore()

    def _draw_arrow(
            self,
            painter: QPainter,
            pos: QPointF,
            scale: float,
            is_forward: bool,
            is_horizontal: bool
    ) -> None:
        """Draws a direction arrow SVG."""
        if not self._arrow_renderer.isValid():
            return

        painter.save()
        painter.translate(pos.x(), pos.y())
        painter.scale(scale, -scale)

        rotation = self._get_arrow_rotation(is_horizontal, is_forward)
        painter.rotate(rotation)

        size = RoadItemStyle.ARROW_BASE_SIZE
        rect = QRectF(-size / 2, -size / 2, size, size)
        self._arrow_renderer.render(painter, rect)

        painter.restore()

    @staticmethod
    def _get_arrow_rotation(is_horizontal: bool, is_forward: bool) -> float:
        """
        Determines arrow rotation angle.
        Assumes SVG source points DOWN (90deg in Qt coords).
        """
        # Mapping: (is_horizontal, is_forward) -> Rotation Angle
        rotation_map = {
            (True, True): -90.0,  # Right
            (True, False): 90.0,  # Left
            (False, True): 180.0,  # Up
            (False, False): 0.0,  # Down
        }
        return rotation_map.get((is_horizontal, is_forward), 0.0)

    # -------------------------------------------------------------------------
    # Geometry Calculation
    # -------------------------------------------------------------------------

    def _recalculate_geometry(self) -> None:
        """Recalculate bounding rect and line paths."""
        road = self._road
        scene_size = DIMENSION.SCENE_SIZE
        lane_width = DIMENSION.LANE_WIDTH

        w_fwd = road.number_of_forward_lanes * lane_width
        w_bwd = road.number_of_backward_lanes * lane_width
        total_width = w_fwd + w_bwd

        if road.orientation == RoadOrientation.HORIZONTAL:
            self._bounding_rect = QRectF(
                -scene_size / 2,
                road.position - w_fwd,
                scene_size,
                total_width,
            )
            center_p1 = QPointF(-scene_size / 2, road.position)
            center_p2 = QPointF(scene_size / 2, road.position)
        else:
            self._bounding_rect = QRectF(
                road.position - w_bwd,
                -scene_size / 2,
                total_width,
                scene_size,
            )
            center_p1 = QPointF(road.position, -scene_size / 2)
            center_p2 = QPointF(road.position, scene_size / 2)

        # Center Line
        self._center_line = QPainterPath()
        if road.number_of_forward_lanes >= 1 and road.number_of_backward_lanes >= 1:
            self._center_line.moveTo(center_p1)
            self._center_line.lineTo(center_p2)

        # Lane Dividers
        self._dashed_lines = QPainterPath()
        self._add_dividers(road.number_of_forward_lanes, is_forward=True, scene_size=scene_size)
        self._add_dividers(road.number_of_backward_lanes, is_forward=False, scene_size=scene_size)

    def _add_dividers(self, num_lanes: int, is_forward: bool, scene_size: int) -> None:
        """Adds dashed divider lines to the painter path."""
        road = self._road
        lane_width = DIMENSION.LANE_WIDTH
        is_horiz = road.orientation == RoadOrientation.HORIZONTAL

        for i in range(1, num_lanes):
            # Calculate offset direction based on lane type
            # Forward usually implies 'minus' in this coordinate system based on prev logic
            offset_val = i * lane_width
            pos_offset = (road.position - offset_val) if is_forward else (road.position + offset_val)

            # For Vertical roads, the logic flips slightly in standard math,
            # but relying on original code's specific logic:
            if not is_horiz:
                # Vertical: Fwd = Pos + Offset, Bwd = Pos - Offset
                pos_offset = (road.position + offset_val) if is_forward else (road.position - offset_val)

            if is_horiz:
                self._dashed_lines.moveTo(-scene_size / 2, pos_offset)
                self._dashed_lines.lineTo(scene_size / 2, pos_offset)
            else:
                self._dashed_lines.moveTo(pos_offset, -scene_size / 2)
                self._dashed_lines.lineTo(pos_offset, scene_size / 2)

    @property
    def position_listeners(self):
        return self._position_listeners
