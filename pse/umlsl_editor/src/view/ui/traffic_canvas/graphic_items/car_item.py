"""
Car graphics item for the UMLSL Traffic Editor.

Provides a visual representation of a car on the traffic canvas, including
position calculation, selection handling, and directional rendering.
"""

import logging
from typing import TYPE_CHECKING, Optional, Tuple

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QPolygonF
from PySide6.QtWidgets import QStyleOptionGraphicsItem, QWidget

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.road_item import RoadItem
from pse.umlsl_editor.src.view.ui.traffic_canvas.graphic_items.selectable_graphics_item import (
    SelectableGraphicsItem,
)
from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION, Z_LAYERS

if TYPE_CHECKING:
    from pse.umlsl_editor.src.controllers import ApplicationController

logger = logging.getLogger(__name__)


class CarItemStyle:
    """Constants and styling configuration for the CarItem."""
    PEN_WIDTH = 0.1
    HOVER_LIGHTNESS = 110
    LABEL_SCALE_THRESHOLD = DIMENSION.GRID_FINE_THRESHOLD


class CarItem(SelectableGraphicsItem):
    """
    Graphics item representing a car on a lane.

    Displays a car as a pentagon shape with directional indicator.
    It subscribes to its parent RoadItem to maintain relative positioning
    when the road moves.

    Coordinate System Note:
        This item assumes a Cartesian coordinate system where Y grows UP.
        Position calculations are centroid-based to remain agnostic to
        rendering transforms.
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
        super().__init__(application_controller)

        self._car = car
        self._road_item = road_item
        self._road = road_item.data(0)

        # Graphics Cache
        self._polygon = QPolygonF()
        self._body_brush = QBrush()
        self._body_pen = QPen()

        # Connect to road movement
        self._road_item.add_position_listener(self)

        self.update_data(car)

    def cleanup(self) -> None:
        """Disconnect listeners before destruction."""
        if self._road_item:
            self._road_item.remove_position_listener(self)

    def update_data(self, car: Car, road_item: Optional[RoadItem] = None) -> None:
        """
        Update the car's display data.

        Args:
            car: The updated car entity.
            road_item: The new road item, if the car changed roads.
        """
        self._car = car
        self.setData(0, car)

        # Handle Road Change
        if road_item is not None and road_item != self._road_item:
            self._road_item.remove_position_listener(self)
            self._road_item = road_item
            self._road = road_item.data(0)
            self._road_item.add_position_listener(self)

        # If road data inside the item changed but item instance is same
        if self._road_item:
            self._road = self._road_item.data(0)

        self.refresh_geometry()

    # -------------------------------------------------------------------------
    # Movement Constraints
    # -------------------------------------------------------------------------

    @staticmethod
    def _get_constraint_for_orientation(orientation: RoadOrientation) -> int:
        """Return the movement axis constraint based on road orientation."""
        if orientation == RoadOrientation.HORIZONTAL:
            return SelectableGraphicsItem.AXIS_X_ONLY
        return SelectableGraphicsItem.AXIS_Y_ONLY

    # -------------------------------------------------------------------------
    # Visual Styling
    # -------------------------------------------------------------------------

    def _update_styles(self) -> None:
        """Configure visual styles based on selection and hover state."""
        self.setZValue(Z_LAYERS.SELECTED_CAR if self.is_selected else Z_LAYERS.CAR)

        # Update constraint in case road orientation changed
        constraint = self._get_constraint_for_orientation(self._road.orientation)
        self.set_movement_constraint(constraint)

        # Color calculation
        base_color = QColor(self._car.color)
        display_color = base_color.lighter() if self.is_selected else base_color

        if self.is_hovered:
            display_color = display_color.lighter(CarItemStyle.HOVER_LIGHTNESS)

        self._body_brush = QBrush(display_color)
        self._body_pen = QPen(display_color.lighter(), CarItemStyle.PEN_WIDTH)

    # -------------------------------------------------------------------------
    # SelectableGraphicsItem Lifecycle Hooks
    # -------------------------------------------------------------------------

    def on_selection_changed(self, is_selected: bool) -> None:
        self._update_styles()
        self.update()

    def on_hover_changed(self, is_hovered: bool) -> None:
        self._update_styles()
        self.update()

    def on_move_committed(self, delta_x: float, delta_y: float) -> None:
        """Handle completed drag movement along the lane."""
        is_horiz = self._road.orientation == RoadOrientation.HORIZONTAL
        delta = delta_x if is_horiz else delta_y

        new_position = self._car.position_on_lane + delta

        self.application_controller.command_controller.edit_car(
            car=self._car,
            position_on_lane=new_position,
        )

    # -------------------------------------------------------------------------
    # Graphics Interface (Qt)
    # -------------------------------------------------------------------------

    def boundingRect(self) -> QRectF:
        return self._polygon.boundingRect()

    def paint(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
            widget: Optional[QWidget] = None,
    ) -> None:
        painter.setPen(self._body_pen)
        painter.setBrush(self._body_brush)
        painter.drawPolygon(self._polygon)

        self._paint_label(painter, option)

    def _paint_label(
            self,
            painter: QPainter,
            option: QStyleOptionGraphicsItem,
    ) -> None:
        """Draw the car's name label centered on the body."""
        transform = painter.worldTransform()
        lod = option.levelOfDetailFromTransform(transform)

        if lod <= CarItemStyle.LABEL_SCALE_THRESHOLD:
            return

        text_scale = 1.0 / lod

        painter.save()

        # Font setup
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(COLORS.BACKGROUND)

        # Center on polygon
        center = self._polygon.boundingRect().center()
        painter.translate(center.x(), center.y())

        # Scale:
        # 1. Apply 'text_scale' to keep size constant relative to screen.
        # 2. Apply -1 to Y to flip the text coordinate system back to "Y-down".
        #    Because the Scene is "Y-up", standard drawText would appear upside down.
        painter.scale(text_scale, -text_scale)

        # Draw centered text
        text = str(self._car.name)
        fm = painter.fontMetrics()
        text_rect = fm.boundingRect(text)

        painter.drawText(
            -text_rect.width() / 2,
            text_rect.height() / 4,  # Visual centering adjustment
            text
        )
        painter.restore()

    # -------------------------------------------------------------------------
    # Geometry Calculation
    # -------------------------------------------------------------------------

    def refresh_geometry(self) -> None:
        """
        Recalculate the car's polygon.
        Called when car data changes or road moves.
        """
        self._update_styles()
        self.prepareGeometryChange()

        center_pos = self._calculate_center_position()
        dimensions = self._calculate_dimensions()

        self._polygon = self._create_centered_polygon(
            center_pos, dimensions, self._road.orientation
        )

        self.update()

    def _calculate_center_position(self) -> Tuple[float, float]:
        """
        Calculate the (Longitudinal, Lateral) center of the car.

        Returns:
            Tuple[float, float]: (position_along_road, position_perpendicular_to_road)
        """
        car = self._car
        road = self._road
        road_item = self._road_item

        lane_width = DIMENSION.LANE_WIDTH

        # 1. Longitudinal Position (Along the road)
        pos_long = car.position_on_lane

        # 2. Lateral Position (Across the road)
        # We calculate the exact center of the lane.

        # Determine offset from Road Center Line
        # Example: Lane 0 is 0.5 widths from center. Lane 1 is 1.5 widths.
        # If your model uses specific signs for Forward/Backward, adapt the sign variable.
        # Here we assume:
        #   Forward lanes are typically Negative Y (Right side in RHT / Y-Up).
        #   Backward lanes are typically Positive Y (Left side).
        #   Using raw lane_index magnitude to determine slot.

        lane_idx = car.lane.lane_index

        is_vertical = road.orientation == RoadOrientation.VERTICAL

        sign = -1 if lane_idx < 0 else 1
        vertical_sign = 1 if is_vertical else -1

        # Center of lane i is at: (i + 0.5) * Width (if i is 0-based)
        # Using abs() to handle negative indices safely
        idx_magnitude = abs(lane_idx)

        # Center offset relative to road midline
        center_offset = (idx_magnitude + 0.5) * lane_width * sign * vertical_sign

        # Add transition offset (lane changing animation)
        transition_offset = car.transition * lane_width

        # Get visual position of the road itself
        road_visual_pos = road.position + (road_item.x() if is_vertical else road_item.y())

        pos_lat = road_visual_pos + center_offset + transition_offset

        return pos_long, pos_lat

    def _calculate_dimensions(self) -> Tuple[float, float]:
        """
        Calculate length and triangle size.
        Returns negative values if the car is visually reversed.
        """
        car_len = self._car.length
        tri_len = DIMENSION.CAR_TRIANGLE_LENGTH

        # Logic for visual direction:
        # If the car is in a backward lane, it faces "Left/Down".
        # Unless speed is negative (reversing in a backward lane = facing Right/Up).
        is_backward_lane = self._car.lane.lane_index < 0
        is_negative_speed = self._car.speed < 0

        if is_backward_lane != is_negative_speed:
            car_len = -car_len
            tri_len = -tri_len

        return car_len, tri_len

    def _create_centered_polygon(
            self,
            center_pos: Tuple[float, float],
            dimensions: Tuple[float, float],
            orientation: RoadOrientation,
    ) -> QPolygonF:
        """
        Create the car polygon relative to its center point.
        This approach works identically for Y-Up or Y-Down systems.
        """
        long_center, lat_center = center_pos
        length, tri_len = dimensions

        half_width = DIMENSION.CAR_WIDTH / 2.0

        # Define the car's local shape relative to its center (0,0)
        # The car body is a rectangle, the front is a triangle.
        # 'length' includes the direction (sign).

        # Calculate X coordinates (Longitudinal)
        # We want the car centered on 'long_center'.
        # Total visual length = abs(length) + abs(tri_len)?
        # Usually 'position' is the center of the car body.

        x_back = -length / 2.0
        x_front = length / 2.0
        x_tip = x_front + tri_len

        # Calculate Y coordinates (Lateral)
        y_top = half_width  # Visual 'Top' (Positive Y)
        y_bot = -half_width  # Visual 'Bottom' (Negative Y)

        # Define points in (Long, Lat) space relative to (0,0)
        local_points = [
            (x_back, y_bot),  # Back-Bottom
            (x_front, y_bot),  # Front-Bottom
            (x_tip, 0.0),  # Tip (Center Y)
            (x_front, y_top),  # Front-Top
            (x_back, y_top)  # Back-Top
        ]

        # Translate to world position and map to orientation
        is_horiz = orientation == RoadOrientation.HORIZONTAL
        poly_points = []

        for local_l, local_w in local_points:
            # Add world center offsets
            final_l = long_center + local_l
            final_w = lat_center + local_w

            if is_horiz:
                # Horizontal Road: Long=X, Lat=Y
                poly_points.append(QPointF(final_l, final_w))
            else:
                # Vertical Road: Long=Y, Lat=X
                poly_points.append(QPointF(final_w, final_l))

        return QPolygonF(poly_points)
