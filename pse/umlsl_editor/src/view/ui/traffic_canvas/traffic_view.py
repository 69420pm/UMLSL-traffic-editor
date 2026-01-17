"""
Traffic view for the UMLSL Traffic Editor.

Custom QGraphicsView with zoom controls, grid background, and coordinate labels.
"""
import math
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QWheelEvent, QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION
from pse.umlsl_editor.src.model.entities.road import RoadOrientation

if TYPE_CHECKING:
    from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_scene import TrafficScene


class TrafficView(QGraphicsView):
    """
    Custom graphics view with zoom constraints, grid background, and coordinate labels.

    Features:
        - Mouse wheel/touchpad zoom with constraints
        - Dynamic grid that adjusts to zoom level
        - Coordinate labels at viewport edges
        - Lane labels for roads
    """

    def __init__(self, scene: QGraphicsScene, parent=None):
        """Initialize the traffic view with default settings."""
        super().__init__(scene, parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setBackgroundBrush(COLORS.GREEN)

        # Initial scale (negative Y to flip coordinate system)
        self.scale(DIMENSION.INITIAL_ZOOM, -DIMENSION.INITIAL_ZOOM)

    def _get_min_scale_for_scene(self) -> float:
        """
        Calculate minimum scale to ensure scene fills the viewport.

        Returns:
            Minimum allowed scale factor.
        """
        viewport_size = self.viewport().size()
        scene_rect = self.scene().sceneRect()

        if scene_rect.width() == 0 or scene_rect.height() == 0:
            return DIMENSION.MIN_ZOOM

        scale_x = viewport_size.width() / scene_rect.width()
        scale_y = viewport_size.height() / scene_rect.height()
        min_scale = max(scale_x, scale_y)

        return max(min_scale, DIMENSION.MIN_ZOOM)

    def resizeEvent(self, event) -> None:
        """Maintain zoom constraints when window is resized."""
        super().resizeEvent(event)
        self._enforce_zoom_constraints()

    def _enforce_zoom_constraints(self) -> None:
        """Clamp zoom level to valid range based on current viewport size."""
        current_scale = abs(self.transform().m11())
        min_scale = self._get_min_scale_for_scene()

        if current_scale < min_scale:
            scale_factor = min_scale / current_scale
            self.scale(scale_factor, scale_factor)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """
        Handle zoom via mouse wheel or touchpad.

        Supports both discrete wheel events and smooth touchpad scrolling.
        """
        pixel_delta = event.pixelDelta().y()
        delta = pixel_delta if pixel_delta != 0 else event.angleDelta().y()

        if delta == 0:
            event.ignore()
            return

        # Adjust sensitivity based on input type
        sensitivity = 0.01 if pixel_delta != 0 else 0.001
        scale_factor = 1 + (delta * sensitivity)

        current_scale = abs(self.transform().m11())
        future_scale = current_scale * scale_factor
        min_scale = self._get_min_scale_for_scene()

        # Clamp scale to valid range
        if future_scale > DIMENSION.MAX_ZOOM:
            scale_factor = DIMENSION.MAX_ZOOM / current_scale
        elif future_scale < min_scale:
            scale_factor = min_scale / current_scale

        self.scale(scale_factor, scale_factor)
        event.accept()

    def _get_grid_step(self) -> float:
        """
        Determine grid spacing based on current zoom level.

        Returns:
            Grid step size in scene units.
        """
        scale = self.transform().m11()
        return DIMENSION.GRID_STEP_COARSE if scale < DIMENSION.GRID_FINE_THRESHOLD else DIMENSION.GRID_STEP_FINE

    @staticmethod
    def _iterate_grid(start: float, end: float, step: float):
        """
        Generate grid coordinates within the given range.

        Args:
            start: Start of the range.
            end: End of the range.
            step: Step size between coordinates.

        Yields:
            Grid coordinate values.
        """
        val = math.floor(start / step) * step
        while val <= end:
            yield val
            val += step

    def _get_visible_bounds(self) -> tuple[float, float, float, float]:
        """
        Get the visible scene area bounds.

        Returns:
            Tuple of (left, right, min_y, max_y).
        """
        visible_scene = self.mapToScene(self.viewport().rect()).boundingRect()
        left, right = visible_scene.left(), visible_scene.right()
        top, bottom = visible_scene.top(), visible_scene.bottom()
        return left, right, min(top, bottom), max(top, bottom)

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        """Draw the grid lines in the background."""
        super().drawBackground(painter, rect)

        viewport_rect = self.viewport().rect()
        step = self._get_grid_step()
        left, right, min_y, max_y = self._get_visible_bounds()

        painter.save()
        painter.resetTransform()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(COLORS.LAYER, DIMENSION.LINE_WIDTH_GRID))

        for x in self._iterate_grid(left, right, step):
            screen_x = int(self.mapFromScene(QPointF(x, 0)).x())
            painter.drawLine(screen_x, 0, screen_x, viewport_rect.height())

        for y in self._iterate_grid(min_y, max_y, step):
            screen_y = int(self.mapFromScene(QPointF(0, y)).y())
            painter.drawLine(0, screen_y, viewport_rect.width(), screen_y)

        painter.restore()

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        """Draw coordinate labels and lane labels at viewport borders."""
        viewport_rect = self.viewport().rect()
        step = self._get_grid_step()
        left, right, min_y, max_y = self._get_visible_bounds()

        painter.save()
        painter.resetTransform()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(COLORS.TEXT))

        # Draw coordinate labels
        for x in self._iterate_grid(left, right, step):
            screen_x = int(self.mapFromScene(QPointF(x, 0)).x())
            painter.drawText(screen_x + 5, viewport_rect.height() - 5, str(int(x)))

        for y in self._iterate_grid(min_y, max_y, step):
            screen_y = int(self.mapFromScene(QPointF(0, y)).y())
            label = str(int(y))
            text_width = painter.fontMetrics().horizontalAdvance(label)
            painter.drawText(viewport_rect.width() - text_width - 5, screen_y - 5, label)

        # Draw lane labels for roads
        self._draw_lane_labels(painter)

        painter.restore()

    def _draw_lane_labels(self, painter: QPainter) -> None:
        """
        Draw lane labels at viewport borders for all roads.

        Draws road names always visible, and lane identifiers when zoomed in.
        """
        scene = self.scene()
        if not hasattr(scene, 'roads'):
            return

        scale = abs(self.transform().m11())
        show_lane_labels = scale >= DIMENSION.LANE_LABEL_MIN_ZOOM
        lane_width = DIMENSION.LANE_WIDTH

        for road in scene.roads:
            road_label, lane_labels = self._get_lane_labels(road, lane_width)

            # Always draw road label
            label, lane_center = road_label
            if road.orientation == RoadOrientation.HORIZONTAL:
                screen_y = int(self.mapFromScene(QPointF(0, lane_center)).y())
                self._draw_label_horizontal(painter, label, screen_y, bold=True)
            else:
                screen_x = int(self.mapFromScene(QPointF(lane_center, 0)).x())
                self._draw_label_vertical(painter, label, screen_x, bold=True)

            # Only draw lane labels if zoomed in enough
            if show_lane_labels:
                for label, lane_center in lane_labels:
                    if road.orientation == RoadOrientation.HORIZONTAL:
                        screen_y = int(self.mapFromScene(QPointF(0, lane_center)).y())
                        self._draw_label_horizontal(painter, label, screen_y)
                    else:
                        screen_x = int(self.mapFromScene(QPointF(lane_center, 0)).x())
                        self._draw_label_vertical(painter, label, screen_x)

    @staticmethod
    def _get_lane_labels(road, lane_width: float) -> tuple[tuple[str, float], list[tuple[str, float]]]:
        """
        Generate road label and lane labels with their positions.

        Args:
            road: The Road entity.
            lane_width: Width of each lane.

        Returns:
            Tuple of (road_label, lane_labels) where each label is (text, position).
        """
        # Road label
        offset = (-0.5 - road.backward_lanes) * lane_width
        center = road.position - offset if road.orientation == RoadOrientation.HORIZONTAL else road.position + offset
        road_label = (road.name, center)

        # Lane labels
        lane_labels = []
        for i in range(road.forward_lanes):
            offset = (i + 0.5) * lane_width
            center = road.position - offset if road.orientation == RoadOrientation.HORIZONTAL else road.position + offset
            lane_labels.append((f"f{i + 1}", center))
        for i in range(road.backward_lanes):
            offset = (i + 0.5) * lane_width
            center = road.position + offset if road.orientation == RoadOrientation.HORIZONTAL else road.position - offset
            lane_labels.append((f"b{i + 1}", center))

        return road_label, lane_labels

    @staticmethod
    def _draw_label_horizontal(painter: QPainter, label: str, screen_y: int, bold: bool = False) -> None:
        """
        Draw a label on the left edge for horizontal roads.

        Args:
            painter: The QPainter to draw with.
            label: Text to draw.
            screen_y: Y position in screen coordinates.
            bold: Whether to draw in bold font.
        """
        if bold:
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
        text_height = painter.fontMetrics().height()
        painter.drawText(5, screen_y + text_height // 4, label)
        if bold:
            font.setBold(False)
            painter.setFont(font)

    @staticmethod
    def _draw_label_vertical(painter: QPainter, label: str, screen_x: int, bold: bool = False) -> None:
        """
        Draw a label on the top edge for vertical roads.

        Args:
            painter: The QPainter to draw with.
            label: Text to draw.
            screen_x: X position in screen coordinates.
            bold: Whether to draw in bold font.
        """
        if bold:
            font = painter.font()
            font.setBold(True)
            painter.setFont(font)
        text_width = painter.fontMetrics().horizontalAdvance(label)
        text_height = painter.fontMetrics().height()
        painter.drawText(screen_x - text_width // 2, text_height, label)
        if bold:
            font.setBold(False)
            painter.setFont(font)

