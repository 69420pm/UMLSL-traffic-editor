# traffic_canvas/graphic_items/road_item.py

from typing import Optional

from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QBrush, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.controllers.view_event_contract import ViewEventHandler
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import (
    SelectableGraphicsItem,
)
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS


class RoadItem(SelectableGraphicsItem):
    """
    Graphics item representing a road with constrained movement based on its
    orientation. Draws asphalt, center line, and lane dividers, and updates
    geometry and z-order when selection or position changes.
    """

    def __init__(self, road: Road, view_event_handler=ViewEventHandler) -> None:
        constraint = self._get_constraint_for_orientation(road.orientation)
        super().__init__(movement_constraint=constraint)

        # Only for testing
        self.view_event_handler = view_event_handler

        self._position_listeners: list = []
        self.setData(0, road)

        self._bounding_rect = QRectF()
        self._center_line = QPainterPath()
        self._dashed_lines = QPainterPath()

        self._setup_styles()
        self.refresh_geometry()

    @staticmethod
    def _get_constraint_for_orientation(orientation: RoadOrientation) -> int:
        """Return the appropriate movement constraint for the given orientation."""
        if orientation == RoadOrientation.HORIZONTAL:
            return SelectableGraphicsItem.AXIS_Y_ONLY
        return SelectableGraphicsItem.AXIS_X_ONLY

    def _setup_styles(self) -> None:
        """Configure visual styles based on selection and hover state."""
        self.setZValue(Z_LAYERS.SELECTED_ROAD if self.is_selected else Z_LAYERS.ROAD)

        color = COLORS.LAYER.lighter() if self.is_selected else COLORS.LAYER

        # Apply hover effect (110% brightness of current state)
        if self.is_hovered:
            color = color.lighter(110)

        self._asphalt_brush = QBrush(color)

        self._center_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._center_pen.setCosmetic(False)

        self._dashed_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._dashed_pen.setStyle(Qt.DashLine)
        self._dashed_pen.setDashPattern([4, 8])
        self._dashed_pen.setCosmetic(False)

    # --- Hooks from SelectableGraphicsItem ---

    def on_selection_changed(self, is_selected: bool) -> None:
        self._setup_styles()

    def on_hover_changed(self, is_hovered: bool) -> None:
        self._setup_styles()

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        road = self.data(0)
        delta = delta_y if road.orientation == RoadOrientation.HORIZONTAL else delta_x
        road.position += delta
        self.view_event_handler.update_road_view(road=road)
        self.update_data(road)

    # --- Position Listener Pattern ---

    def add_position_listener(self, listener) -> None:
        """Register an object to be notified when this road moves."""
        if listener not in self._position_listeners:
            self._position_listeners.append(listener)

    def _notify_listeners(self) -> None:
        """Notify all registered listeners to refresh their geometry."""
        for listener in self._position_listeners:
            listener.refresh_geometry()

    def itemChange(self, change, value):
        """Notify listeners after position changes."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._notify_listeners()
        return super().itemChange(change, value)

    # --- Graphics Interface ---

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
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

    def _paint_labels(self, painter: QPainter, option: QStyleOptionGraphicsItem) -> None:
        """Draws road/lane labels that stick to the viewport edges."""

        # 1. Calculate Level of Detail (Zoom)
        #    Use the painter's transform directly.
        transform = painter.worldTransform()
        lod = option.levelOfDetailFromTransform(transform)

        # 2. Map Screen (0,0) to Item Coordinates
        #    We don't need 'option.widget' to know where (0,0) is.
        #    We just invert the matrix that maps Item->Screen.
        inv_transform, invertible = transform.inverted()
        if not invertible:
            return

        # 'screen_top_left' is the point in *Item Space* that corresponds
        # to the top-left pixel of the view.
        screen_top_left = inv_transform.map(QPointF(0, 0))

        # 3. Calculate Sticky Positions
        text_scale = 1.0 / lod
        padding = 10 * text_scale

        visible_left = screen_top_left.x() + padding
        visible_top = screen_top_left.y() - padding

        # 4. Draw Logic
        road = self.data(0)
        lane_width = DIMENSION.LANE_WIDTH
        is_horizontal = road.orientation == RoadOrientation.HORIZONTAL

        painter.save()
        painter.setPen(COLORS.TEXT)

        font = painter.font()
        font.setBold(False)
        painter.setFont(font)

        # Helper to draw text right-side up
        def draw_sticky_label(text: str, cx: float, cy: float):
            painter.save()
            painter.translate(cx, cy)
            # Flip Y axis back so text is upright
            painter.scale(text_scale, -text_scale)

            fm = painter.fontMetrics()
            rect = fm.boundingRect(text)
            # Center text on the anchor point
            painter.drawText(-rect.width() / 2, rect.height() / 4, text)
            painter.restore()


        # --- Draw Road Name ---
        font.setBold(True)
        painter.setFont(font)

        vertical_offset = 8 * text_scale
        horizontal_offset = 16 * text_scale

        if is_horizontal:
            name_y = road.position + vertical_offset + (road.backward_lanes * lane_width)
            draw_sticky_label(road.name, visible_left, name_y)
        else:
            name_x = road.position - (road.backward_lanes*lane_width) - horizontal_offset
            draw_sticky_label(road.name, name_x, visible_top)

        painter.restore()

        # Don't render lane labels if we are too zoomed out
        if lod <= DIMENSION.GRID_FINE_THRESHOLD:
            return


        # --- Draw Lane Labels ---

        # Forward Lanes
        for i in range(road.forward_lanes):
            lane_offset = (i + 0.5) * lane_width
            if is_horizontal:
                # Stick X to visible_left, Keep Y centered on lane
                draw_sticky_label(f"f{i + 1}", visible_left, road.position - lane_offset)
            else:
                # Stick Y to visible_top, Keep X centered on lane
                draw_sticky_label(f"f{i + 1}", road.position + lane_offset, visible_top)

        # Backward Lanes
        for i in range(road.backward_lanes):
            lane_offset = (i + 0.5) * lane_width
            if is_horizontal:
                draw_sticky_label(f"b{i + 1}", visible_left, road.position + lane_offset)
            else:
                draw_sticky_label(f"b{i + 1}", road.position - lane_offset, visible_top)

    def update_data(self, road: Road) -> None:
        """Update the road data and refresh all visual elements."""
        self.setData(0, road)
        self.set_movement_constraint(self._get_constraint_for_orientation(road.orientation))
        self.refresh_geometry()
        self._notify_listeners()

    def refresh_geometry(self) -> None:
        """Recalculate all geometry based on current road data."""
        self.prepareGeometryChange()

        road = self.data(0)
        self._calculate_bounding_rect(road)
        self._calculate_center_line(road)
        self._calculate_lane_dividers(road)

        self.update()

    def _calculate_bounding_rect(self, road: Road) -> None:
        """Calculate the road's bounding rectangle."""
        lane_width = DIMENSION.LANE_WIDTH
        scene_size = DIMENSION.SCENE_SIZE
        half_scene = scene_size / 2

        forward_width = road.forward_lanes * lane_width
        backward_width = road.backward_lanes * lane_width
        total_width = forward_width + backward_width

        if road.orientation == RoadOrientation.HORIZONTAL:
            y_start = road.position - forward_width
            self._bounding_rect = QRectF(-half_scene, y_start, scene_size, total_width)
        else:
            x_start = road.position - backward_width
            self._bounding_rect = QRectF(x_start, -half_scene, total_width, scene_size)

    def _calculate_center_line(self, road: Road) -> None:
        """Calculate the center line path between forward and backward lanes."""
        self._center_line = QPainterPath()

        # Only draw center line if there are lanes in both directions
        if road.forward_lanes < 1 or road.backward_lanes < 1:
            return

        half_scene = DIMENSION.SCENE_SIZE / 2

        if road.orientation == RoadOrientation.HORIZONTAL:
            self._center_line.moveTo(-half_scene, road.position)
            self._center_line.lineTo(half_scene, road.position)
        else:
            self._center_line.moveTo(road.position, -half_scene)
            self._center_line.lineTo(road.position, half_scene)

    def _calculate_lane_dividers(self, road: Road) -> None:
        """Calculate dashed divider lines between lanes in the same direction."""
        self._dashed_lines = QPainterPath()

        lane_width = DIMENSION.LANE_WIDTH
        half_scene = DIMENSION.SCENE_SIZE / 2
        is_horizontal = road.orientation == RoadOrientation.HORIZONTAL

        # Calculate dividers for forward lanes
        for i in range(1, road.forward_lanes):
            offset = road.position - (i * lane_width) if is_horizontal else road.position + (i * lane_width)
            self._add_divider_line(offset, half_scene, is_horizontal)

        # Calculate dividers for backward lanes
        for i in range(1, road.backward_lanes):
            offset = road.position + (i * lane_width) if is_horizontal else road.position - (i * lane_width)
            self._add_divider_line(offset, half_scene, is_horizontal)

    def _add_divider_line(self, offset: float, half_scene: float, is_horizontal: bool) -> None:
        """Add a single divider line to the dashed lines path."""
        if is_horizontal:
            self._dashed_lines.moveTo(-half_scene, offset)
            self._dashed_lines.lineTo(half_scene, offset)
        else:
            self._dashed_lines.moveTo(offset, -half_scene)
            self._dashed_lines.lineTo(offset, half_scene)
