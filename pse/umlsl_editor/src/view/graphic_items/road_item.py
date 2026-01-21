# --- Concrete Road Item ---
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainterPath, QPen, QBrush, QPainter
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.entities.road import RoadOrientation, Road
from pse.umlsl_editor.src.view.graphic_items.selectable_graphics_item import SelectableGraphicsItem
from pse.umlsl_editor.src.view.view_constants import Z_LAYERS, COLORS, DIMENSION


class RoadItem(SelectableGraphicsItem):
    """
    Concrete implementation for displaying a Road.
    """

    def __init__(self, road: Road):
        # Determine initial constraint based on orientation
        constraint = (
            SelectableGraphicsItem.AXIS_Y_ONLY
            if road.orientation == RoadOrientation.HORIZONTAL
            else SelectableGraphicsItem.AXIS_X_ONLY
        )

        super().__init__(movement_constraint=constraint)

        self._road = road
        self._bounding_rect = QRectF()
        self._center_line = QPainterPath()
        self._dashed_lines = QPainterPath()

        self._setup_styles()
        self._recalculate_geometry()

    def _setup_styles(self):
        self.setZValue(Z_LAYERS.ROAD)
        # Use parent's selection state
        color = COLORS.LAYER.lighter() if self._is_selected else COLORS.LAYER
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

    def on_move_committed(self, delta_x: float, delta_y: float):
        # Calculate new position based on the delta
        # Note: Because of axis locking, one of these deltas will be 0 (or very close)
        if self._road.orientation == RoadOrientation.HORIZONTAL:
            new_position = self._road.position + delta_y
        else:
            new_position = self._road.position + delta_x

        # Create new road object
        new_road = Road(
            uid=self._road.uid,
            name=self._road.name,
            orientation=self._road.orientation,
            position=new_position,
            forward_lanes=self._road.forward_lanes,
            backward_lanes=self._road.backward_lanes

        )
        self.update_data(new_road)

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

    def update_data(self, road: Road):
        self._road = road

        # Update constraint in case orientation changed
        new_constraint = (
            SelectableGraphicsItem.AXIS_Y_ONLY
            if road.orientation == RoadOrientation.HORIZONTAL
            else SelectableGraphicsItem.AXIS_X_ONLY
        )
        self.set_movement_constraint(new_constraint)

        self.prepareGeometryChange()
        self._recalculate_geometry()
        self.update()

    def _recalculate_geometry(self) -> None:
        road = self._road
        scene_size = DIMENSION.SCENE_SIZE
        lane_width = DIMENSION.LANE_WIDTH

        width_f = road.forward_lanes * lane_width
        width_b = road.backward_lanes * lane_width

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
        if road.forward_lanes >= 1 and road.backward_lanes >= 1:
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