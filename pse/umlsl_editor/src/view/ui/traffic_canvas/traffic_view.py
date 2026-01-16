import math
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainter, QWheelEvent, QPen
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene

from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION


class TrafficView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # Apply Constants
        self.setBackgroundBrush(COLORS.GREEN)
        self.scale(1, -1)

    def wheelEvent(self, event: QWheelEvent):
        # Determine delta (touchpad vs mouse wheel)
        pixel_delta = event.pixelDelta().y()
        delta = pixel_delta if pixel_delta != 0 else event.angleDelta().y()

        if delta == 0:
            event.ignore()
            return

        sensitivity = 0.01 if pixel_delta != 0 else 0.001
        scale_factor = 1 + (delta * sensitivity)

        # Calculate Future Scale to enforce limits
        current_scale = self.transform().m11()
        future_scale = current_scale * scale_factor

        if future_scale > 6.0:
            scale_factor = 6.0 / current_scale
        elif future_scale < 0.45:
            scale_factor = 0.45 / current_scale

        self.scale(scale_factor, scale_factor)
        event.accept()

    def drawForeground(self, painter: QPainter, rect: QRectF):
        viewport_rect = self.viewport().rect()
        base_step = DIMENSION.LANE_WIDTH

        painter.save()
        painter.resetTransform()  # Draw in Screen Pixels
        painter.setRenderHint(QPainter.Antialiasing)

        # 1. Determine Visible Scene Area
        visible_scene = self.mapToScene(viewport_rect).boundingRect()
        left, right = visible_scene.left(), visible_scene.right()
        # Handle Y-axis flipping (min/max ensures correct loop order)
        top, bottom = visible_scene.top(), visible_scene.bottom()
        min_y, max_y = min(top, bottom), max(top, bottom)

        # Helper to generate grid coordinates
        def iterate_grid(start, end):
            val = math.floor(start / base_step) * base_step
            while val <= end:
                yield val
                val += base_step

        # --- PASS 1: DRAW ALL LINES (Background) ---
        painter.setPen(QPen(COLORS.LAYER, 1))

        # Vertical Lines
        for x in iterate_grid(left, right):
            screen_x = int(self.mapFromScene(QPointF(x, 0)).x())
            painter.drawLine(screen_x, 0, screen_x, viewport_rect.height())

        # Horizontal Lines
        for y in iterate_grid(min_y, max_y):
            screen_y = int(self.mapFromScene(QPointF(0, y)).y())
            painter.drawLine(0, screen_y, viewport_rect.width(), screen_y)

        # --- PASS 2: DRAW ALL TEXT (Foreground) ---
        # Text is drawn last so it sits ON TOP of all lines
        text_pen = QPen(COLORS.TEXT)
        painter.setPen(text_pen)

        # X-Axis Labels (Bottom)
        for x in iterate_grid(left, right):
            screen_x = int(self.mapFromScene(QPointF(x, 0)).x())
            label = str(int(x / base_step))
            # Offset text slightly to not overlap the vertical line exactly
            painter.drawText(screen_x + 5, viewport_rect.height() - 5, label)

        # Y-Axis Labels (Right)
        for y in iterate_grid(min_y, max_y):
            screen_y = int(self.mapFromScene(QPointF(0, y)).y())
            label = str(int(y / base_step))

            # Calculate text width to align to the right edge
            text_width = painter.fontMetrics().horizontalAdvance(label)
            painter.drawText(viewport_rect.width() - text_width - 5, screen_y - 5, label)

        painter.restore()