"""
Custom QGraphicsView with zoom and pan capabilities for the traffic canvas.
"""
from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QWheelEvent, QMouseEvent


class TrafficCanvasView(QGraphicsView):
    """
    A custom QGraphicsView that supports zooming and panning.
    """

    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self._zoom_factor = 1.15
        self._pan_start = QPointF()
        self._is_panning = False

        # Enable smooth transformations
        self.setRenderHint(self.RenderHint.Antialiasing)
        self.setRenderHint(self.RenderHint.SmoothPixmapTransform)

        # Enable dragging with middle mouse button
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

    def wheelEvent(self, event: QWheelEvent):
        """Handle mouse wheel for zooming."""
        # Get the angle delta (positive = zoom in, negative = zoom out)
        delta = event.angleDelta().y()

        if delta > 0:
            # Zoom in
            self.scale(self._zoom_factor, self._zoom_factor)
        else:
            # Zoom out
            self.scale(1 / self._zoom_factor, 1 / self._zoom_factor)

        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press for panning."""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Start panning
            self._is_panning = True
            self._pan_start = event.pos()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move for panning."""
        if self._is_panning:
            # Calculate the delta movement
            delta = event.pos() - self._pan_start
            self._pan_start = event.pos()

            # Pan the view
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release for panning."""
        if event.button() == Qt.MouseButton.MiddleButton:
            # Stop panning
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

