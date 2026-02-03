"""
Road graphics item for the UMLSL Traffic Editor.

Provides a visual representation of a road on the traffic canvas, including
lane dividers, center lines, and sticky labels that remain visible at
viewport edges.
"""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QBrush, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import (
    SelectableGraphicsItem,
)
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController


class RoadItem(SelectableGraphicsItem):
    """
    Graphics item representing a road with multiple lanes.

    Displays a road spanning the scene with:
        - Asphalt background colored by selection/hover state
        - Solid center line separating forward and backward lanes
        - Dashed lane dividers between lanes in the same direction
        - Sticky labels that remain visible at viewport edges

    The road can be dragged perpendicular to its orientation to change
    its position.

    Attributes:
        position_listeners: List of items to notify when the road moves.
    """

    def __init__(
            self,
            road: Road,
            application_controller: "ApplicationController",
    ) -> None:
        """
        Initialize the road graphics item.

        Args:
            road: The road entity to display.
            application_controller: The application controller for commands.
        """
        super().__init__(application_controller)

        self.position_listeners = []
        self._road = road
        self._bounding_rect = QRectF()
        self._center_line = QPainterPath()
        self._dashed_lines = QPainterPath()

        self._asphalt_brush = QBrush()
        self._center_pen = QPen()
        self._dashed_pen = QPen()

        self.update_data(road)

    def update_data(self, road: Road) -> None:
        """
        Update the road's display data.

        Args:
            road: The updated road entity.
        """
        self._road = road
        self.setData(0, road)

        # This ensures selection state is valid if the road orientation changed
        super().check_current_selection()

        constraint = self._get_constraint_for_orientation(road.orientation)
        self.set_movement_constraint(constraint)

        self._setup_styles()
        self.prepareGeometryChange()
        self._recalculate_geometry()
        self.update()

        self._notify_listeners()

    # -------------------------------------------------------------------------
    # Movement Constraints
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_constraint_for_orientation(orientation: RoadOrientation) -> int:
        """
        Get the movement constraint for the given road orientation.

        Roads can only move perpendicular to their orientation.

        Args:
            orientation: The road's orientation.

        Returns:
            The axis constraint constant for movement.
        """
        if orientation == RoadOrientation.HORIZONTAL:
            return SelectableGraphicsItem.AXIS_Y_ONLY
        return SelectableGraphicsItem.AXIS_X_ONLY

    # -------------------------------------------------------------------------
    # Visual Styling
    # -------------------------------------------------------------------------

    def _setup_styles(self) -> None:
        """Configure visual styles based on selection and hover state."""
        self.setZValue(Z_LAYERS.SELECTED_ROAD if self.is_selected else Z_LAYERS.ROAD)

        color = COLORS.LAYER.lighter() if self.is_selected else COLORS.LAYER
        if self.is_hovered:
            color = color.lighter(110)

        self._asphalt_brush = QBrush(color)

        self._center_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._center_pen.setCosmetic(False)

        self._dashed_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._dashed_pen.setStyle(Qt.DashLine)
        self._dashed_pen.setDashPattern([4, 8])
        self._dashed_pen.setCosmetic(False)

    # -------------------------------------------------------------------------
    # SelectableGraphicsItem Hooks
    # -------------------------------------------------------------------------

    def on_selection_changed(self, is_selected: bool) -> None:
        """Handle selection state change."""
        self._setup_styles()

    def on_hover_changed(self, is_hovered: bool) -> None:
        """Handle hover state change."""
        self._setup_styles()

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        """
        Handle completed drag movement.

        Updates the road's position based on the drag delta.

        Args:
            delta_x: The horizontal movement delta.
            delta_y: The vertical movement delta.
        """
        if self._road.orientation == RoadOrientation.HORIZONTAL:
            new_position = self._road.position + delta_y
        else:
            new_position = self._road.position + delta_x

        self.application_controller.command_controller.update_road(
            road=self._road,
            position=new_position,
        )

    # -------------------------------------------------------------------------
    # Position Listeners
    # -------------------------------------------------------------------------

    def add_position_listener(self, listener) -> None:
        """
        Register an object to be notified when this road moves.

        Args:
            listener: An object with a refresh_geometry() method.
        """
        if listener not in self.position_listeners:
            self.position_listeners.append(listener)

    def remove_position_listener(self, listener) -> None:
        """
        Unregister an object from position change notifications.

        Args:
            listener: The listener to remove.
        """
        if listener in self.position_listeners:
            self.position_listeners.remove(listener)

    def _notify_listeners(self) -> None:
        """Notify all registered listeners that the road has moved."""
        for listener in self.position_listeners:
            listener.refresh_geometry()

    def itemChange(self, change, value):
        """
        Handle item changes, notifying listeners on position updates.

        Args:
            change: The type of change occurring.
            value: The new value for the change.

        Returns:
            The potentially modified value.
        """
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._notify_listeners()

        return super().itemChange(change, value)

    # -------------------------------------------------------------------------
    # Graphics Interface
    # -------------------------------------------------------------------------

    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the road."""
        return self._bounding_rect

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        """
        Paint the road including asphalt, lane dividers, and labels.

        Args:
            painter: The QPainter to use for drawing.
            option: Style options for the item.
            widget: The widget being painted on.
        """
        # Draw asphalt background
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._asphalt_brush)
        painter.drawRect(self._bounding_rect)

        # Draw center line
        painter.setPen(self._center_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self._center_line)

        # Draw lane dividers
        painter.setPen(self._dashed_pen)
        painter.drawPath(self._dashed_lines)

        self._paint_labels(painter, option)

    # -------------------------------------------------------------------------
    # Label Painting
    # -------------------------------------------------------------------------

    def _paint_labels(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
    ) -> None:
        """
        Draw road and lane labels that stick to the viewport edges.

        Labels remain visible at the edge of the viewport regardless of
        how much of the road is currently visible.

        Args:
            painter: The QPainter to use for drawing.
            option: Style options containing transform info.
        """
        transform = painter.worldTransform()
        lod = option.levelOfDetailFromTransform(transform)

        inv_transform, invertible = transform.inverted()
        if not invertible:
            return

        screen_top_left = inv_transform.map(QPointF(0, 0))

        text_scale = 1.0 / lod
        padding = 10 * text_scale

        visible_left = screen_top_left.x() + padding
        visible_top = screen_top_left.y() - padding

        road = self.data(0)
        lane_width = DIMENSION.LANE_WIDTH
        is_horizontal = road.orientation == RoadOrientation.HORIZONTAL

        painter.save()
        painter.setPen(COLORS.TEXT)

        self._paint_road_name(
            painter, road, text_scale, visible_left, visible_top, is_horizontal
        )

        if lod > DIMENSION.GRID_FINE_THRESHOLD:
            self._paint_lane_labels(
                painter, road, lane_width, text_scale, visible_left, visible_top, is_horizontal
            )

        painter.restore()

    def _paint_road_name(
            self,
            painter: QPainter,
            road: Road,
            text_scale: float,
            visible_left: float,
            visible_top: float,
            is_horizontal: bool,
    ) -> None:
        """
        Draw the road name label.

        Args:
            painter: The QPainter to use for drawing.
            road: The road entity.
            text_scale: Scale factor for text size.
            visible_left: The left edge of the visible area in scene coords.
            visible_top: The top edge of the visible area in scene coords.
            is_horizontal: True if the road is horizontal.
        """
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)

        vertical_offset = 8 * text_scale
        horizontal_offset = 16 * text_scale
        lane_width = DIMENSION.LANE_WIDTH

        if is_horizontal:
            name_y = road.position + vertical_offset + (
                    road.number_of_backward_lanes * lane_width
            )
            self._draw_sticky_label(painter, road.name, visible_left, name_y, text_scale)
        else:
            name_x = road.position - (
                    road.number_of_backward_lanes * lane_width
            ) - horizontal_offset
            self._draw_sticky_label(painter, road.name, name_x, visible_top, text_scale)

    def _paint_lane_labels(
            self,
            painter: QPainter,
            road: Road,
            lane_width: float,
            text_scale: float,
            visible_left: float,
            visible_top: float,
            is_horizontal: bool,
    ) -> None:
        """
        Draw lane labels for forward and backward lanes.

        Args:
            painter: The QPainter to use for drawing.
            road: The road entity.
            lane_width: The width of each lane.
            text_scale: Scale factor for text size.
            visible_left: The left edge of the visible area in scene coords.
            visible_top: The top edge of the visible area in scene coords.
            is_horizontal: True if the road is horizontal.
        """
        font = painter.font()
        font.setBold(False)
        painter.setFont(font)

        # Forward lanes
        for i in range(road.number_of_forward_lanes):
            lane_offset = (i + 0.5) * lane_width
            label = f"f{i + 1}"

            if is_horizontal:
                self._draw_sticky_label(
                    painter, label, visible_left, road.position - lane_offset, text_scale
                )
            else:
                self._draw_sticky_label(
                    painter, label, road.position + lane_offset, visible_top, text_scale
                )

        # Backward lanes
        for i in range(road.number_of_backward_lanes):
            lane_offset = (i + 0.5) * lane_width
            label = f"b{i + 1}"

            if is_horizontal:
                self._draw_sticky_label(
                    painter, label, visible_left, road.position + lane_offset, text_scale
                )
            else:
                self._draw_sticky_label(
                    painter, label, road.position - lane_offset, visible_top, text_scale
                )

    def _draw_sticky_label(
            self,
            painter: QPainter,
            text: str,
            cx: float,
            cy: float,
            text_scale: float,
    ) -> None:
        """
        Draw a label that remains upright regardless of view transform.

        Args:
            painter: The QPainter to use for drawing.
            text: The text to display.
            cx: The x-coordinate for the label center.
            cy: The y-coordinate for the label center.
            text_scale: Scale factor for text size.
        """
        painter.save()
        painter.translate(cx, cy)
        painter.scale(text_scale, -text_scale)

        fm = painter.fontMetrics()
        rect = fm.boundingRect(text)

        painter.drawText(-rect.width() / 2, rect.height() / 4, text)
        painter.restore()

    # -------------------------------------------------------------------------
    # Geometry Calculation
    # -------------------------------------------------------------------------

    def _recalculate_geometry(self) -> None:
        """Recalculate the road's bounding rect, center line, and lane dividers."""
        road = self.data(0)
        scene_size = DIMENSION.SCENE_SIZE
        lane_width = DIMENSION.LANE_WIDTH

        width_forward = road.number_of_forward_lanes * lane_width
        width_backward = road.number_of_backward_lanes * lane_width

        if road.orientation == RoadOrientation.HORIZONTAL:
            y_start = road.position - width_forward
            self._bounding_rect = QRectF(
                -scene_size / 2,
                y_start,
                scene_size,
                width_forward + width_backward,
            )
        else:
            x_start = road.position - width_backward
            self._bounding_rect = QRectF(
                x_start,
                -scene_size / 2,
                width_forward + width_backward,
                scene_size,
            )

        self._calculate_center_line(road, scene_size)
        self._calculate_lane_dividers(road, scene_size)

    def _calculate_center_line(self, road: Road, scene_size: int) -> None:
        """
        Calculate the center line path between forward and backward lanes.

        Args:
            road: The road entity.
            scene_size: The size of the scene.
        """
        self._center_line = QPainterPath()

        if road.number_of_forward_lanes < 1 or road.number_of_backward_lanes < 1:
            return

        if road.orientation == RoadOrientation.HORIZONTAL:
            self._center_line.moveTo(-scene_size / 2, road.position)
            self._center_line.lineTo(scene_size / 2, road.position)
        else:
            self._center_line.moveTo(road.position, -scene_size / 2)
            self._center_line.lineTo(road.position, scene_size / 2)

    def _calculate_lane_dividers(self, road: Road, scene_size: int) -> None:
        """
        Calculate the dashed lane divider paths.

        Args:
            road: The road entity.
            scene_size: The size of the scene.
        """
        self._dashed_lines = QPainterPath()
        lane_width = DIMENSION.LANE_WIDTH

        # Forward lane dividers
        for i in range(1, road.number_of_forward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                offset = road.position - (i * lane_width)
            else:
                offset = road.position + (i * lane_width)
            self._add_divider_line(road.orientation, offset, scene_size)

        # Backward lane dividers
        for i in range(1, road.number_of_backward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                offset = road.position + (i * lane_width)
            else:
                offset = road.position - (i * lane_width)
            self._add_divider_line(road.orientation, offset, scene_size)

    def _add_divider_line(
            self,
            orientation: RoadOrientation,
            offset: float,
            scene_size: int,
    ) -> None:
        """
        Add a divider line to the dashed lines path.

        Args:
            orientation: The road orientation.
            offset: The perpendicular offset for the divider.
            scene_size: The size of the scene.
        """
        if orientation == RoadOrientation.HORIZONTAL:
            self._dashed_lines.moveTo(-scene_size / 2, offset)
            self._dashed_lines.lineTo(scene_size / 2, offset)
        else:
            self._dashed_lines.moveTo(offset, -scene_size / 2)
            self._dashed_lines.lineTo(offset, scene_size / 2)
