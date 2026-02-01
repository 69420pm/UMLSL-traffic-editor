# traffic_canvas/graphic_items/road_item.py

from PySide6.QtCore import QRectF, Qt, QPointF
from PySide6.QtGui import QPainterPath, QPen, QBrush, QPainter
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget, QGraphicsItem

from pse.umlsl_editor.src.model.entities.road import RoadOrientation, Road
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import SelectableGraphicsItem
from pse.umlsl_editor.src.view.view_constants import Z_LAYERS, COLORS, DIMENSION


class RoadItem(SelectableGraphicsItem):
    """
    Concrete implementation for displaying a Road.
    """

    def __init__(self, road: Road):

        super().__init__()

        self.position_listeners = []
        self._road = road
        self._bounding_rect = QRectF()
        self._center_line = QPainterPath()
        self._dashed_lines = QPainterPath()

        self.update_data(road)

    def update_data(self, road: Road):
        self._road = road
        self.setData(0, road)

        # Update constraint in case orientation changed
        new_constraint = (
            SelectableGraphicsItem.AXIS_Y_ONLY
            if road.orientation == RoadOrientation.HORIZONTAL
            else SelectableGraphicsItem.AXIS_X_ONLY
        )
        self.set_movement_constraint(new_constraint)
        self._setup_styles()
        self.prepareGeometryChange()
        self._recalculate_geometry()
        self.update()

        # Notify listeners because the model data (absolute position) changed
        self._notify_listeners()

    def _setup_styles(self):
        self.setZValue(Z_LAYERS.SELECTED_ROAD if self.is_selected else Z_LAYERS.ROAD)
        # Use parent's selection state
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

    # --- Implement Hooks from SelectableGraphicsItem ---

    def on_selection_changed(self, is_selected: bool):
        # Re-run style setup to switch colors
        self._setup_styles()

    def on_hover_changed(self, is_hovered: bool) -> None:
        self._setup_styles()

    def on_move_committed(self, delta_x: float, delta_y: float):
        # Calculate new position based on the delta
        current_road = self.data(0)

        if current_road.orientation == RoadOrientation.HORIZONTAL:
            new_position = current_road.position + delta_y
        else:
            new_position = current_road.position + delta_x

        # Create new road object
        self.data(0).position = new_position
        self.update_data(self.data(0))

    # --- Update Crossings Logic ---

    def add_position_listener(self, listener):
        """Registers an object to be notified when this road moves."""
        if listener not in self.position_listeners:
            self.position_listeners.append(listener)

    def remove_position_listener(self, listener):
        """Unregisters an object from position change notifications."""
        if listener in self.position_listeners:
            self.position_listeners.remove(listener)

    def _notify_listeners(self):
        for listener in self.position_listeners:
            listener.refresh_geometry()

    def itemChange(self, change, value):
        """Override to notify listeners on position change."""
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._notify_listeners()

        return super().itemChange(change, value)

    # --- Standard Graphics Logic ---

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._asphalt_brush)
        painter.drawRect(self._bounding_rect)

        painter.setPen(self._center_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(self._center_line)

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
            name_y = road.position + vertical_offset + (road.number_of_backward_lanes * lane_width)
            draw_sticky_label(road.name, visible_left, name_y)
        else:
            name_x = road.position - (road.number_of_backward_lanes * lane_width) - horizontal_offset
            draw_sticky_label(road.name, name_x, visible_top)

        painter.restore()

        # Don't render lane labels if we are too zoomed out
        if lod <= DIMENSION.GRID_FINE_THRESHOLD:
            return

        # --- Draw Lane Labels ---

        # Forward Lanes
        for i in range(road.number_of_forward_lanes):
            lane_offset = (i + 0.5) * lane_width
            if is_horizontal:
                # Stick X to visible_left, Keep Y centered on lane
                draw_sticky_label(f"f{i + 1}", visible_left, road.position - lane_offset)
            else:
                # Stick Y to visible_top, Keep X centered on lane
                draw_sticky_label(f"f{i + 1}", road.position + lane_offset, visible_top)

        # Backward Lanes
        for i in range(road.number_of_backward_lanes):
            lane_offset = (i + 0.5) * lane_width
            if is_horizontal:
                draw_sticky_label(f"b{i + 1}", visible_left, road.position + lane_offset)
            else:
                draw_sticky_label(f"b{i + 1}", road.position - lane_offset, visible_top)

    def _recalculate_geometry(self) -> None:
        road = self.data(0)
        scene_size = DIMENSION.SCENE_SIZE
        lane_width = DIMENSION.LANE_WIDTH

        width_f = road.number_of_forward_lanes * lane_width
        width_b = road.number_of_backward_lanes * lane_width

        if road.orientation == RoadOrientation.HORIZONTAL:
            # Horizontal road: Spans X axis (scene_size), positioned on Y axis
            y_start = road.position - width_f
            rect = QRectF(-scene_size / 2, y_start, scene_size, width_f + width_b)
        else:
            # Vertical road: Spans Y axis (scene_size), positioned on X axis
            x_start = road.position - width_b
            rect = QRectF(x_start, -scene_size / 2, width_f + width_b, scene_size)

        self._bounding_rect = rect
        self._calculate_center_line(road, scene_size)
        self._calculate_lane_dividers(road, scene_size)

    def _calculate_center_line(self, road: Road, scene_size: int) -> None:
        if road.number_of_forward_lanes >= 1 and road.number_of_backward_lanes >= 1:
            self._center_line = QPainterPath()
            if road.orientation == RoadOrientation.HORIZONTAL:
                self._center_line.moveTo(-scene_size / 2, road.position)
                self._center_line.lineTo(scene_size / 2, road.position)
            else:
                self._center_line.moveTo(road.position, -scene_size / 2)
                self._center_line.lineTo(road.position, scene_size / 2)

    def _calculate_lane_dividers(self, road: Road, scene_size: int) -> None:
        self._dashed_lines = QPainterPath()
        lane_width = DIMENSION.LANE_WIDTH

        def add_divider(offset: float) -> None:
            if road.orientation == RoadOrientation.HORIZONTAL:
                self._dashed_lines.moveTo(-scene_size / 2, offset)
                self._dashed_lines.lineTo(scene_size / 2, offset)
            else:
                self._dashed_lines.moveTo(offset, -scene_size / 2)
                self._dashed_lines.lineTo(offset, scene_size / 2)

        for i in range(1, road.number_of_forward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                add_divider(road.position - (i * lane_width))
            else:
                add_divider(road.position + (i * lane_width))

        for i in range(1, road.number_of_backward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                add_divider(road.position + (i * lane_width))
            else:
                add_divider(road.position - (i * lane_width))
