"""
Traffic view for the UMLSL Traffic Editor.

Custom QGraphicsView with zoom controls, grid background, and coordinate labels.
"""
import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter, QPen, QWheelEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QSizeGrip

from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic_scene import TrafficScene
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION


class TrafficView(QGraphicsView):
    """
    Custom graphics view with zoom constraints, grid background, and coordinate labels.

    Features:
        - Mouse wheel/touchpad zoom with constraints
        - Dynamic grid that adjusts to zoom level
        - Coordinate labels at viewport edges
        - Lane labels for roads
    """

    # -------------------------------------------------------------------------
    # Initialization
    # -------------------------------------------------------------------------

    def __init__(self, scene: QGraphicsScene, parent=None):
        """Initialize the traffic view with default settings."""
        super().__init__(scene, parent)

        self._configure_view()
        self.scale(DIMENSION.INITIAL_ZOOM, -DIMENSION.INITIAL_ZOOM)


    def _configure_view(self) -> None:
        """Configure view settings for rendering and interaction."""
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setBackgroundBrush(COLORS.GREEN)

    # -------------------------------------------------------------------------
    # Zoom Handling
    # -------------------------------------------------------------------------

    def button_zoom(self, amount: float) -> None:
        #set anchor to center
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

        scale_factor = self._calculate_clamped_scale(amount)
        self.scale(scale_factor, scale_factor)

        self._enforce_zoom_constraints()


    def resizeEvent(self, event) -> None:
        """Maintain zoom constraints when window is resized."""
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        super().resizeEvent(event)
        self._enforce_zoom_constraints()

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle zoom via mouse wheel or touchpad."""
        delta = event.pixelDelta().y() or event.angleDelta().y()
        if delta == 0:
            event.ignore()
            return

        is_touchpad = event.pixelDelta().y() != 0
        sensitivity = DIMENSION.TOUCHPAD_ZOOM_SENSITIVITY if is_touchpad else DIMENSION.WHEEL_ZOOM_SENSITIVITY
        scale_factor = self._calculate_clamped_scale(1 + delta * sensitivity)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.scale(scale_factor, scale_factor)
        event.accept()

    def _calculate_clamped_scale(self, scale_factor: float) -> float:
        """Clamp scale factor to keep zoom within valid range."""
        current_scale = abs(self.transform().m11())
        future_scale = current_scale * scale_factor
        min_scale = self._get_min_scale_for_scene()

        if future_scale > DIMENSION.MAX_ZOOM:
            return DIMENSION.MAX_ZOOM / current_scale
        if future_scale < min_scale:
            return min_scale / current_scale
        return scale_factor

    def _enforce_zoom_constraints(self) -> None:
        """Clamp zoom level to valid range based on current viewport size."""
        current_scale = abs(self.transform().m11())
        min_scale = self._get_min_scale_for_scene()

        if current_scale < min_scale:
            self.scale(min_scale / current_scale, min_scale / current_scale)

    def _get_min_scale_for_scene(self) -> float:
        """Calculate minimum scale to ensure scene fills the viewport."""
        viewport_size = self.viewport().size()
        scene_rect = self.scene().sceneRect()

        if scene_rect.width() == 0 or scene_rect.height() == 0:
            return DIMENSION.MIN_ZOOM

        scale_x = viewport_size.width() / scene_rect.width()
        scale_y = viewport_size.height() / scene_rect.height()
        return max(scale_x, scale_y, DIMENSION.MIN_ZOOM)

    # -------------------------------------------------------------------------
    # Grid Drawing
    # -------------------------------------------------------------------------

    def drawBackground(self, painter: QPainter, rect: QRectF) -> None:
        """Draw the grid lines in the background."""
        super().drawBackground(painter, rect)
        self._draw_grid(painter, QPen(COLORS.LAYER, DIMENSION.LANE_WIDTH))

    def _draw_grid(self, painter: QPainter, pen: QPen) -> None:
        """Draw grid lines across the viewport."""
        viewport_rect = self.viewport().rect()
        step = self._get_grid_step()
        left, right, min_y, max_y = self._get_visible_bounds()

        painter.save()
        painter.resetTransform()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(pen)

        for x in self._iter_grid_values(left, right, step):
            screen_x = int(self.mapFromScene(QPointF(x, 0)).x())
            painter.drawLine(screen_x, 0, screen_x, viewport_rect.height())

        for y in self._iter_grid_values(min_y, max_y, step):
            screen_y = int(self.mapFromScene(QPointF(0, y)).y())
            painter.drawLine(0, screen_y, viewport_rect.width(), screen_y)

        painter.restore()

    def _get_grid_step(self) -> float:
        """Determine grid spacing based on current zoom level."""
        scale = self.transform().m11()
        return DIMENSION.GRID_STEP_COARSE if scale <= DIMENSION.GRID_FINE_THRESHOLD else DIMENSION.GRID_STEP_FINE

    # -------------------------------------------------------------------------
    # Foreground Labels
    # -------------------------------------------------------------------------

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        """Draw coordinate labels and lane labels at viewport borders."""
        painter.save()
        painter.resetTransform()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QPen(COLORS.TEXT))

        self._draw_coordinate_labels(painter)

        painter.restore()

    def _draw_coordinate_labels(self, painter: QPainter) -> None:
        """Draw X and Y coordinate labels at viewport edges."""
        viewport_rect = self.viewport().rect()
        step = self._get_grid_step()
        left, right, min_y, max_y = self._get_visible_bounds()

        # X-axis labels (bottom edge)
        for x in self._iter_grid_values(left, right, step):
            screen_x = int(self.mapFromScene(QPointF(x, 0)).x())
            painter.drawText(screen_x + DIMENSION.LABEL_PADDING, viewport_rect.height() - DIMENSION.LABEL_PADDING, str(int(x)))

        # Y-axis labels (right edge)
        for y in self._iter_grid_values(min_y, max_y, step):
            screen_y = int(self.mapFromScene(QPointF(0, y)).y())
            label = str(int(y))
            text_width = painter.fontMetrics().horizontalAdvance(label)
            painter.drawText(viewport_rect.width() - text_width - DIMENSION.LABEL_PADDING, screen_y - DIMENSION.LABEL_PADDING, label)

    # -------------------------------------------------------------------------
    # Utility Methods
    # -------------------------------------------------------------------------

    def _get_visible_bounds(self) -> tuple[float, float, float, float]:
        """Get the visible scene area as (left, right, min_y, max_y)."""
        visible_scene = self.mapToScene(self.viewport().rect()).boundingRect()
        left, right = visible_scene.left(), visible_scene.right()
        top, bottom = visible_scene.top(), visible_scene.bottom()
        return left, right, min(top, bottom), max(top, bottom)

    @staticmethod
    def _iter_grid_values(start: float, end: float, step: float):
        """Yield grid coordinate values within the given range."""
        val = math.floor(start / step) * step
        while val <= end:
            yield val
            val += step
