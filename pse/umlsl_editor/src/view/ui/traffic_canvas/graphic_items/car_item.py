"""
Car graphics item for the UMLSL Traffic Editor.

Provides a visual representation of a car on the traffic canvas, including
position calculation, selection handling, and directional rendering.
"""

from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import (
    SelectableGraphicsItem,
)
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController


class CarItem(SelectableGraphicsItem):
    """
    Graphics item representing a car on a lane.

    Displays a car as a pentagon shape with directional indicator, positioned
    on its assigned lane. Supports selection, hover effects, and dragging
    constrained to the lane's orientation.

    The car shape includes:
        - A rectangular body
        - A triangular front indicating travel direction

    Attributes:
        road_item: The RoadItem graphics item for the car's current road.
    """

    def __init__(
        self,
        car: Car,
        road_item: RoadItem,
        application_controller: "ApplicationController",
    ) -> None:
        """
        Initialize the car graphics item.

        Args:
            car: The car entity to display.
            road_item: The road item the car is positioned on.
            application_controller: The application controller for commands.
        """
        self._car = car
        self._polygon = QPolygonF()
        self.road_item = road_item
        self._road = road_item.data(0)

        self._body_brush = QBrush()
        self._body_pen = QPen()

        super().__init__(application_controller)
        self.update_data(car)

    def update_data(self, car: Car, road_item: Optional[RoadItem] = None) -> None:
        """
        Update the car's display data.

        Args:
            car: The updated car entity.
            road_item: The new road item, if the car changed roads.
        """
        self._car = car
        self.setData(0, car)

        if road_item is not None:
            self.road_item = road_item
            self._road = road_item.data(0)

        self.refresh_geometry()

    # -------------------------------------------------------------------------
    # Movement Constraints
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_constraint_for_orientation(orientation: RoadOrientation) -> int:
        """
        Get the movement constraint for the given road orientation.

        Args:
            orientation: The road's orientation.

        Returns:
            The axis constraint constant for movement.
        """
        if orientation == RoadOrientation.HORIZONTAL:
            return SelectableGraphicsItem.AXIS_X_ONLY
        return SelectableGraphicsItem.AXIS_Y_ONLY

    # -------------------------------------------------------------------------
    # Visual Styling
    # -------------------------------------------------------------------------

    def _setup_styles(self) -> None:
        """Configure visual styles based on selection and hover state."""
        self.setZValue(Z_LAYERS.SELECTED_CAR if self.is_selected else Z_LAYERS.CAR)

        constraint = self._get_constraint_for_orientation(self._road.orientation)
        self.set_movement_constraint(constraint)

        car_color = QColor(self.data(0).color)
        color = car_color.lighter() if self.is_selected else car_color

        if self.is_hovered:
            color = color.lighter(110)

        self._body_brush = QBrush(color)
        self._body_pen = QPen(color.lighter(), 0.1)

    # -------------------------------------------------------------------------
    # SelectableGraphicsItem Hooks
    # -------------------------------------------------------------------------

    def on_selection_changed(self, is_selected: bool) -> None:
        """Handle selection state change."""
        self._setup_styles()

    def on_hover_changed(self, is_hovered: bool) -> None:
        """Handle hover state change."""
        self._setup_styles()

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        """
        Handle completed drag movement.

        Updates the car's position along its lane based on the drag delta.

        Args:
            delta_x: The horizontal movement delta.
            delta_y: The vertical movement delta.
        """
        if self._road.orientation == RoadOrientation.HORIZONTAL:
            delta = delta_x
        else:
            delta = delta_y

        new_position = self._car.position_on_lane + delta
        self.application_controller.command_controller.edit_car(
            car=self._car,
            position_on_lane=new_position,
        )

    # -------------------------------------------------------------------------
    # Graphics Interface
    # -------------------------------------------------------------------------

    def boundingRect(self) -> QRectF:
        """Return the bounding rectangle of the car shape."""
        return self._polygon.boundingRect()

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """
        Paint the car shape.

        Args:
            painter: The QPainter to use for drawing.
            option: Style options for the item.
            widget: The widget being painted on.
        """
        painter.setPen(self._body_pen)
        painter.setBrush(self._body_brush)
        painter.drawPolygon(self._polygon)

        self._paint_label(painter, option)

    def _paint_label(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
    ) -> None:
        """
        Draw the car's name label centered on the car body.

        The label is scaled and flipped to remain readable regardless of
        the view's transform.

        Args:
            painter: The QPainter to use for drawing.
            option: Style options containing level of detail info.
        """
        transform = painter.worldTransform()
        lod = option.levelOfDetailFromTransform(transform)

        if lod <= DIMENSION.GRID_FINE_THRESHOLD:
            return

        text_scale = 1.0 / lod
        car = self.data(0)
        text = str(car.name)

        painter.save()

        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(COLORS.BACKGROUND)

        center = self._polygon.boundingRect().center()
        painter.translate(center.x(), center.y())

        # Scale and flip Y to counteract the view's Y-flip
        painter.scale(text_scale, -text_scale)

        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(text)

        x_pos = -text_rect.center().x()
        y_pos = -text_rect.center().y()

        painter.drawText(x_pos, y_pos, text)
        painter.restore()

    # -------------------------------------------------------------------------
    # Geometry Calculation
    # -------------------------------------------------------------------------

    def refresh_geometry(self) -> None:
        """Recalculate the car's polygon based on current position and lane."""
        self._setup_styles()
        self.prepareGeometryChange()

        position = self._calculate_car_position(
            self._car, self._road, self.road_item
        )
        dimensions = self._calculate_car_dimensions(self._car)

        self._polygon = self._create_car_polygon(
            position, dimensions, self._road.orientation
        )

        self.update()

    def _calculate_car_position(
        self,
        car: Car,
        road: Road,
        road_item: RoadItem,
    ) -> tuple[float, float]:
        """
        Calculate the car's position in scene coordinates.

        Args:
            car: The car entity.
            road: The road entity the car is on.
            road_item: The road's graphics item.

        Returns:
            Tuple of (x, y) position coordinates.
        """
        lane_width = DIMENSION.LANE_WIDTH
        car_width = DIMENSION.CAR_WIDTH

        x = car.position_on_lane

        if road.orientation == RoadOrientation.VERTICAL:
            lane_index = -car.lane.lane_index
        else:
            lane_index = -car.lane.lane_index

        lane_offset = (
            lane_width * lane_index - (lane_width - car_width) / 2.0 - car_width
        )

        if road.orientation == RoadOrientation.VERTICAL:
            road_offset = road.position + road_item.x()
        else:
            road_offset = road.position + road_item.y()

        y = lane_offset + road_offset

        return x, y

    @staticmethod
    def _calculate_car_dimensions(car: Car) -> tuple[float, float]:
        """
        Calculate the car's length and triangle dimensions based on direction.

        The car shape is flipped when traveling in the backward direction.

        Args:
            car: The car entity.

        Returns:
            Tuple of (car_length, triangle_length) with sign indicating direction.
        """
        car_length = car.length
        triangle_length = DIMENSION.CAR_TRIANGLE_LENGTH

        is_backward = car.lane.lane_index < 0
        is_negative_velocity = car.speed < 0

        # Flip direction if exactly one condition is true (XOR)
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
        """
        Create the pentagon polygon representing the car shape.

        The car consists of a rectangular body with a triangular front
        pointing in the direction of travel.

        Args:
            position: The (x, y) base position of the car.
            dimensions: The (car_length, triangle_length) dimensions.
            orientation: The road orientation for coordinate transformation.

        Returns:
            A QPolygonF defining the car shape.
        """
        x, y = position
        car_length, triangle_length = dimensions
        car_width = DIMENSION.CAR_WIDTH
        is_horizontal = orientation == RoadOrientation.HORIZONTAL

        points = [
            self._orient_point(x, y, is_horizontal),
            self._orient_point(x + car_length, y, is_horizontal),
            self._orient_point(
                x + car_length + triangle_length, y + car_width / 2, is_horizontal
            ),
            self._orient_point(x + car_length, y + car_width, is_horizontal),
            self._orient_point(x, y + car_width, is_horizontal),
        ]

        return QPolygonF(points)

    @staticmethod
    def _orient_point(a: float, b: float, is_horizontal: bool) -> QPointF:
        """
        Transform coordinates based on road orientation.

        For horizontal roads, coordinates are used as-is (a=x, b=y).
        For vertical roads, coordinates are swapped (a=y, b=x).

        Args:
            a: The first coordinate value.
            b: The second coordinate value.
            is_horizontal: True if the road is horizontal.

        Returns:
            A QPointF with appropriately oriented coordinates.
        """
        if is_horizontal:
            return QPointF(a, b)
        return QPointF(b, a)
