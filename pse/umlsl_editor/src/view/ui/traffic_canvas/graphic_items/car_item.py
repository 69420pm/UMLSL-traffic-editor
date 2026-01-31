from typing import Optional

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import (
    SelectableGraphicsItem,
)
from pse.umlsl_editor.src.view.view_constants import DIMENSION, Z_LAYERS, COLORS


class CarItem(SelectableGraphicsItem):
    """
    Graphics item representing a car on a lane, with constrained movement based
    on its road orientation and selection state.
    """

    def __init__(self, car: Car, data_controller: DataController):
        self._car = car
        self._road = data_controller.get_road_by_uid(car.lane.road_uid)

        constraint = self._get_constraint_for_orientation(self._road.orientation.opposite)
        super().__init__(movement_constraint=constraint)
        self.setData(0, car)

        self._position_listeners: list = []

        self.polygon = QPolygonF()

        self._setup_styles()
        self.refresh_geometry()

    @staticmethod
    def _get_constraint_for_orientation(orientation: RoadOrientation) -> int:
        """Return the appropriate movement constraint for the given orientation."""
        if orientation == RoadOrientation.HORIZONTAL:
            return SelectableGraphicsItem.AXIS_X_ONLY
        return SelectableGraphicsItem.AXIS_Y_ONLY

    def _setup_styles(self) -> None:
        """Configure visual styles based on selection and hover state."""
        self.setZValue(Z_LAYERS.SELECTED_CAR if self.is_selected else Z_LAYERS.CAR)

        car_color = QColor(self.data(0).color)
        color = car_color.lighter() if self.is_selected else car_color

        # Apply hover effect (110% brightness of current state)
        if self.is_hovered:
            color = color.lighter(110)

        self._body_brush = QBrush(color)
        self._body_pen = QPen(color.lighter(), 0.1)

    # --- Hooks from SelectableGraphicsItem ---

    def on_selection_changed(self, is_selected: bool) -> None:
        self._setup_styles()

    def on_hover_changed(self, is_hovered: bool) -> None:
        self._setup_styles()

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        car = self.data(0)
        delta = delta_y if self._orientation == RoadOrientation.VERTICAL else delta_x
        car.position_on_lane += delta
        self.update_data(car)

    # --- Position Listener Pattern ---

    def add_position_listener(self, listener) -> None:
        """Register an object to be notified when this car moves."""
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
        return self.polygon.boundingRect()

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        painter.setPen(self._body_pen)
        painter.setBrush(self._body_brush)
        painter.drawPolygon(self.polygon)

        # Draw Label
        self._paint_label(painter, option)

    def _paint_label(self, painter: QPainter, option: QStyleOptionGraphicsItem) -> None:
        """Draws the car ID centered exactly within the car body."""
        # 1. Check Level of Detail to optimize performance
        transform = painter.worldTransform()
        lod = option.levelOfDetailFromTransform(transform)
        if lod <= DIMENSION.GRID_FINE_THRESHOLD: return

        text_scale = 1.0 / lod
        car = self.data(0)
        text = str(car.name)

        painter.save()
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(COLORS.BACKGROUND)

        # 2. Move to the visual center of the car
        #    Using the polygon bounding rect ensures we find the middle of the shape
        center = self.polygon.boundingRect().center()
        painter.translate(center.x(), center.y())

        # 3. Scale and Flip
        #    We scale by (1, -1) to counteract the View's Y-flip.
        #    This ensures standard 'Screen Coordinates' for text drawing.
        painter.scale(text_scale, -text_scale)

        # 4. Calculate Exact Centering
        #    Get the tight bounding box of the text string (e.g., "C1")
        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(text)

        #    Calculate the position that places the center of text_rect at (0,0)
        #    text_rect.center() is usually something like (width/2, -height/2) relative to baseline.
        #    We negate it to shift the drawing origin.
        x_pos = -text_rect.center().x()
        y_pos = -text_rect.center().y()

        painter.drawText(x_pos, y_pos, text)

        painter.restore()

    def update_data(self, car: Car) -> None:
        """Update the car data and refresh all visual elements."""
        self._car = car
        self.setData(0, car)
        self.refresh_geometry()
        self._notify_listeners()

    def refresh_geometry(self) -> None:
        """Recalculate polygon geometry based on current car data."""
        self.prepareGeometryChange()

        position = self._calculate_car_position(self._car, self._road, self.road_item)
        dimensions = self._calculate_car_dimensions(self._car)

        self.polygon = self._create_car_polygon(position, dimensions, self._road.orientation)
        self.update()

    def _calculate_car_position(self, car: Car, road, road_item: RoadItem) -> tuple[float, float]:
        """Calculate the car's x, y position based on lane and road data."""
        lane_width = DIMENSION.LANE_WIDTH
        car_width = DIMENSION.CAR_WIDTH

        x = car.position_on_lane

        lane_index = -car.lane.lane_index if road.orientation == RoadOrientation.VERTICAL else -car.lane.lane_index + 1

        # Calculate lane offset within the road
        lane_offset = lane_width * lane_index - (lane_width - car_width) / 2.0

        if road.orientation == RoadOrientation.HORIZONTAL:
            road_offset = road_item.y()
            y = road.position - lane_offset + road_offset
        else:
            road_offset = road_item.x()
            y = road.position - lane_offset + road_offset

        return x, y

    @staticmethod
    def _calculate_car_dimensions(car: Car) -> tuple[float, float]:
        """Calculate effective car length and triangle length based on direction."""
        car_length = car.length
        triangle_length = DIMENSION.CAR_TRIANGLE_LENGTH

        # Determine if we need to flip the car direction
        is_backward = car.lane.lane_index < 0
        is_negative_velocity = car.speed < 0

        # XOR: flip direction if exactly one condition is true
        if is_backward != is_negative_velocity:
            car_length = -car_length
            triangle_length = -triangle_length

        return car_length, triangle_length

    def _create_car_polygon(
            self,
            position: tuple[float, float],
            dimensions: tuple[float, float],
            orientation: RoadOrientation,
    ) -> QPolygonF:
        """Create the pentagon polygon representing the car shape."""
        x, y = position
        car_length, triangle_length = dimensions
        car_width = DIMENSION.CAR_WIDTH
        is_horizontal = orientation == RoadOrientation.HORIZONTAL

        # Define points in local coordinate space, then transform based on orientation
        points = [
            self._orient_point(x, y, is_horizontal),
            self._orient_point(x + car_length, y, is_horizontal),
            self._orient_point(x + car_length + triangle_length, y + car_width / 2, is_horizontal),
            self._orient_point(x + car_length, y + car_width, is_horizontal),
            self._orient_point(x, y + car_width, is_horizontal),
        ]

        return QPolygonF(points)

    @staticmethod
    def _orient_point(a: float, b: float, is_horizontal: bool) -> QPointF:
        """Transform coordinates based on road orientation."""
        if is_horizontal:
            return QPointF(a, b)
        return QPointF(b, a)
