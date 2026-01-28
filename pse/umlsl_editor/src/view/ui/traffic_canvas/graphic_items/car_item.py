from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainterPath, QPen, QBrush, QPainter
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget, QGraphicsItem

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation, Road
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import SelectableGraphicsItem
from pse.umlsl_editor.src.view.view_constants import Z_LAYERS, COLORS, DIMENSION


class CarItem(SelectableGraphicsItem):
    """
    Concrete implementation for displaying a Road.
    """

    def __init__(self, car: Car, roads: dict[str, RoadItem]):
        # Determine initial constraint based on orientation
        constraint = (
            SelectableGraphicsItem.AXIS_X_ONLY
            if roads[car.lane.road_uid].data(0).orientation == RoadOrientation.HORIZONTAL
            else SelectableGraphicsItem.AXIS_Y_ONLY
        )

        super().__init__(movement_constraint=constraint)

        self._position_listeners = []
        self.setData(0, car)
        self.setData(1, roads)

        self._bounding_rect = QRectF()

        self._setup_styles()
        self.refresh_geometry()

    def _setup_styles(self):
        self.setZValue(Z_LAYERS.SELECTED_CAR if self.is_selected else Z_LAYERS.CAR)
        # Use parent's selection state
        color = COLORS.RED.lighter() if self.is_selected else COLORS.RED
        self._body_brush = QBrush(color)

    # --- Implement Hooks from SelectableGraphicsItem ---

    def on_selection_changed(self, is_selected: bool):
        # Re-run style setup to switch colors
        self._setup_styles()

    def on_move_committed(self, delta_x: float, delta_y: float):
        # Calculate new position based on the delta
        pass

    # --- Update Crossings Logic ---

    def add_position_listener(self, listener):
        """Registers an object to be notified when this road moves."""
        if listener not in self._position_listeners:
            self._position_listeners.append(listener)

    def _notify_listeners(self):
        for listener in self._position_listeners:
            listener.refresh_geometry()

    def itemChange(self, change, value):
        """Override to notify listeners on position change."""
        # FIX: Use ItemPositionHasChanged (fired AFTER update) instead of ItemPositionChange (fired BEFORE)
        if change == QGraphicsItem.ItemPositionHasChanged:
            self._notify_listeners()

        return super().itemChange(change, value)

    # --- Standard Graphics Logic ---

    def boundingRect(self) -> QRectF:
        return self._bounding_rect

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None):
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._body_brush)
        painter.drawRect(self._bounding_rect)

    def update_data(self, car: Car):
        self.setData(0, car)
        self.prepareGeometryChange()
        self.refresh_geometry()
        self.update()

        # Notify listeners because the model data (absolute position) changed
        self._notify_listeners()

    def refresh_geometry(self) -> None:
        car = self.data(0)
        road = self.data(1)[car.lane.road_uid].data(0)

        lane_width = DIMENSION.LANE_WIDTH

        x = car.position_on_lane
        y = road.position + lane_width * car.lane.lane_index


        if road.orientation == RoadOrientation.HORIZONTAL:
            rect = QRectF(x,y,car.length, lane_width*.9)
        else:
            rect = QRectF(y, x, lane_width*.9, car.length)

        self._bounding_rect = rect