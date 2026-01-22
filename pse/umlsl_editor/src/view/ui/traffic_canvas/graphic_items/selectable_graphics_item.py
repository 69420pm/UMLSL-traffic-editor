# view/items/road_item.py

from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QGraphicsView
from PySide6.QtCore import QRectF, Qt, QPoint, QPointF
from PySide6.QtGui import QPainter, QPainterPath, QPen, QBrush

from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation


# --- Base Class ---
class SelectableGraphicsItem(QGraphicsItem):
    """
    Base class that handles:
    1. Selection (Click to toggle).
    2. Dragging Selected -> Moves Item (Constrained).
    3. Dragging Unselected -> Pans the View (No selection change).
    """

    AXIS_FREE = 0
    AXIS_X_ONLY = 1
    AXIS_Y_ONLY = 2

    def __init__(self, movement_constraint=AXIS_FREE):
        super().__init__()
        self.is_selected = False
        self._movement_constraint = movement_constraint

        # State tracking
        self._drag_start_pos = None  # Scene pos (for item drag check)
        self._pan_start_screen_pos = None  # Screen pos (for view panning)
        self._is_panning_active = False  # Flag to distinguish Panning from Clicking

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)

    def set_movement_constraint(self, constraint):
        self._movement_constraint = constraint

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value
            current_pos = self.pos()
            if self._movement_constraint == self.AXIS_X_ONLY:
                new_pos.setY(current_pos.y())
            elif self._movement_constraint == self.AXIS_Y_ONLY:
                new_pos.setX(current_pos.x())
            return new_pos
        return super().itemChange(change, value)

    def mousePressEvent(self, event):
        # 1. Reset state
        self._drag_start_pos = event.scenePos()
        self._pan_start_screen_pos = event.screenPos()
        self._is_panning_active = False

        # 2. Logic: Only allow ITEM movement if selected.
        self.setFlag(QGraphicsItem.ItemIsMovable, self.is_selected)

        super().mousePressEvent(event)
        event.accept()

    def mouseMoveEvent(self, event):
        if self.is_selected:
            # --- Scenario A: Selected -> Move Item ---

            super().mouseMoveEvent(event)
        else:
            # --- Scenario B: Not Selected -> Pan View ---
            current_screen_pos = event.screenPos()
            delta = current_screen_pos - self._pan_start_screen_pos

            # Only trigger pan if we moved slightly (filters out jitter)
            if delta.manhattanLength() > 2 or self._is_panning_active:
                self._is_panning_active = True
                self._pan_start_screen_pos = current_screen_pos

                # Perform the scroll
                view_viewport = event.widget()
                if view_viewport and view_viewport.parent():
                    view = view_viewport.parent()
                    if isinstance(view, QGraphicsView):
                        hs = view.horizontalScrollBar()
                        vs = view.verticalScrollBar()
                        hs.setValue(hs.value() - delta.x())
                        vs.setValue(vs.value() - delta.y())

    def mouseReleaseEvent(self, event):
        # 1. Check if we were panning (dragging unselected)
        if self._is_panning_active:
            # We just finished panning the scene.
            # Do NOT toggle selection.
            # Ensure the item didn't accidentally move locally.
            if self.pos().manhattanLength() > 0:
                self.setPos(0, 0)
            return  # Exit early

        # 2. Standard Logic: Check for Item Drag or Click
        scene_drag_dist = (event.scenePos() - self._drag_start_pos).manhattanLength()
        was_item_dragged = scene_drag_dist > 0
        has_moved_visually = self.pos().manhattanLength() > 0

        # --- CASE: Item Drag Committed (Selected & Moved) ---
        if was_item_dragged and self.is_selected and has_moved_visually:
            self.on_move_committed(self.x(), self.y())
            self.setPos(0, 0)

        # --- CASE: Click (No Drag, No Pan) ---
        elif not was_item_dragged:
            # Snap back if any micro-movement occurred
            if has_moved_visually:
                self.setPos(0, 0)

            # Toggle Selection
            self.is_selected = not self.is_selected
            self.on_selection_changed(self.is_selected)
            self.update()

        super().mouseReleaseEvent(event)

    def on_move_committed(self, delta_x: float, delta_y: float):
        pass

    def on_selection_changed(self, is_selected: bool):
        pass