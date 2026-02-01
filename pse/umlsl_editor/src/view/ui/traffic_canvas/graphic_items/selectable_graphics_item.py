# view/ui/traffic_canvas/graphic_items/selectable_graphics_item.py
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QGraphicsItem, QGraphicsView

from pse.umlsl_editor.src.controllers import ApplicationController


class SelectableGraphicsItem(QGraphicsItem):
    """
    Base class that provides:
    1. Selection toggling on click.
    2. Dragging when selected with optional axis constraints.
    3. View panning when dragging an unselected item (no selection change).
    """

    AXIS_FREE = 0
    AXIS_X_ONLY = 1
    AXIS_Y_ONLY = 2

    def __init__(self, application_controller: "ApplicationController"):
        super().__init__()
        self._view_event_handler = None
        self.is_selected = False
        self.is_hovered = False
        self._movement_constraint = self.AXIS_FREE
        self.application_controller = application_controller

        self.application_controller.view_event_handler.get_on_selection_changed_signal().connect(
            self._on_global_selection_change)

        # State tracking
        self._drag_start_pos = None
        self._pan_start_screen_pos = None
        self._is_panning = False

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

    def set_movement_constraint(self, constraint: int) -> None:
        """Set the axis constraint for item movement."""
        self._movement_constraint = constraint

    def itemChange(self, change: int, value):
        """Apply movement constraints when the item position changes."""
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value
            current_pos = self.pos()

            if self._movement_constraint == self.AXIS_X_ONLY:
                new_pos.setY(current_pos.y())
            elif self._movement_constraint == self.AXIS_Y_ONLY:
                new_pos.setX(current_pos.x())

            return new_pos

        return super().itemChange(change, value)

        # --- Hover Events ---

    def hoverEnterEvent(self, event) -> None:
        """Update cursor and state when mouse enters."""
        self.is_hovered = True
        self._update_cursor_state()
        self.on_hover_changed(True)
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event) -> None:
        """Reset cursor and state when mouse leaves."""
        self.is_hovered = False
        self.setCursor(Qt.ArrowCursor)  # Reset to default
        self.on_hover_changed(False)
        super().hoverLeaveEvent(event)

    def _update_cursor_state(self) -> None:
        """Set the cursor based on the current selection state."""
        if self.is_selected:
            # Indicates the item is ready to be moved
            self.setCursor(Qt.OpenHandCursor)
        else:
            # Indicates the item is clickable (to select) but not immediately movable
            self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event) -> None:
        """Initialize drag/pan and set 'Grabbing' cursor."""
        self._drag_start_pos = event.scenePos()
        self._pan_start_screen_pos = event.screenPos()
        self._is_panning = False

        # Visual feedback: We are now grabbing the item or the canvas
        self.setCursor(Qt.ClosedHandCursor)

        # Only allow item movement if already selected
        self.setFlag(QGraphicsItem.ItemIsMovable, self.is_selected)

        super().mousePressEvent(event)
        event.accept()

    def mouseReleaseEvent(self, event) -> None:
        """Handle release and restore the appropriate hover cursor."""
        if self._is_panning:
            self._finish_panning()
        else:
            self._handle_drag_or_click(event)

        # Restore cursor (OpenHand if selected, PointingHand if not)
        self._update_cursor_state()
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event) -> None:
        """Handle item dragging (if selected) or view panning (if not selected)."""
        if self.is_selected:
            super().mouseMoveEvent(event)
        else:
            self._handle_view_panning(event)

    def _handle_view_panning(self, event) -> None:
        """Pan the view when dragging an unselected item."""
        current_screen_pos = event.screenPos()
        delta = current_screen_pos - self._pan_start_screen_pos

        if delta.manhattanLength() > 0 or self._is_panning:
            self._is_panning = True
            self._pan_start_screen_pos = current_screen_pos
            self._apply_scroll_delta(event.widget(), delta)

    def _apply_scroll_delta(self, viewport, delta) -> None:
        """Apply scroll delta to the parent view's scrollbars."""
        if not viewport or not viewport.parent():
            return

        view = viewport.parent()
        if not isinstance(view, QGraphicsView):
            return

        h_scroll = view.horizontalScrollBar()
        v_scroll = view.verticalScrollBar()
        h_scroll.setValue(h_scroll.value() - delta.x())
        v_scroll.setValue(v_scroll.value() - delta.y())

    def _finish_panning(self) -> None:
        if self._has_moved():
            self.setPos(0, 0)

    def _handle_drag_or_click(self, event) -> None:
        """Distinguish between item drag and click, then handle appropriately."""
        drag_distance = (event.scenePos() - self._drag_start_pos).manhattanLength()
        was_dragged = drag_distance > 0

        if was_dragged and self.is_selected and self._has_moved():
            self._commit_move()
        elif not was_dragged:
            self._toggle_selection()

    def _has_moved(self) -> bool:
        """Check if the item has moved from its original position."""
        return self.pos().manhattanLength() > 0

    def _commit_move(self) -> None:
        """Commit the item movement and reset local position."""
        self.on_move_committed(self.x(), self.y())
        self.setPos(0, 0)

    @Slot(str)
    def _on_global_selection_change(self, selected_uid: str):
        """Slot: Called when ANY item is selected anywhere in the app."""
        # Get the entity stored in this item (assuming setData(0, entity) is used)
        entity = self.data(0)
        if not entity:
            return

        should_be_selected = (entity.uid == selected_uid)

        # Only trigger update if state actually changes
        if self.is_selected != should_be_selected:
            self.is_selected = should_be_selected
            self.on_selection_changed(self.is_selected)
            self._update_cursor_state()
            self.update()

    # Modify the existing _toggle_selection or mouse handler
    def _toggle_selection(self) -> None:
        entity = self.data(0)
        
        if self.is_selected:
            self.application_controller.command_controller.clear_selection()
        else:
            self.application_controller.command_controller.select_entity(entity.uid)

    # --- Hooks for Subclasses ---

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        """Called when an item drag is completed. Override in subclasses."""
        pass

    def on_selection_changed(self, is_selected: bool) -> None:
        """Called when selection state changes. Override in subclasses."""
        pass

    def on_hover_changed(self, is_hovered: bool) -> None:
        """Called when hover state changes. Override in subclasses."""
        pass
