"""
Car view model for the UMLSL Traffic Editor.

Calculates geometry for rendering cars and their reserved crossing areas.
"""
from PySide6.QtCore import QRectF, QPointF
from PySide6.QtGui import QPainterPath, QColor, QPolygonF

from pse.umlsl_editor.src.view.view_constants import DIMENSION, COLORS
from pse.umlsl_editor.src.view.view_models.entity_view_model import EntityViewModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import RoadOrientation


class CarViewModel(EntityViewModel[Car]):
    """
    View model for Car entities.

    Calculates car position on the road based on lane and position.
    Also computes reserved crossing areas for visualization.
    """

    def __init__(self, car: Car, road_accessor):
        """
        Initialize the car view model.

        Args:
            car: The Car domain entity.
            road_accessor: Object providing road lookup by name.
        """
        self._road_accessor = road_accessor
        self._reserved_shapes: list[QPolygonF] = []
        super().__init__(car)

    @property
    def reserved_shapes(self) -> list[QPolygonF]:
        """Return polygons representing reserved intersection areas."""
        return self._reserved_shapes

    def recalculate(self) -> None:
        """Recalculate car geometry based on lane and position."""
        car = self._data

        road = self._road_accessor.get_road(car.lane.road_name)
        if not road:
            return

        lane_w = DIMENSION.LANE_WIDTH
        car_w = DIMENSION.CAR_WIDTH

        # Calculate car body position
        total_road_width = (road.forward_lanes + road.backward_lanes) * lane_w
        road_start_transverse = road.position - (total_road_width / 2)
        lane_offset = road_start_transverse + (car.lane.lane_index * lane_w)
        center_offset = (lane_w - car_w) / 2

        if road.orientation == RoadOrientation.HORIZONTAL:
            x = car.position_on_lane
            y = lane_offset + center_offset
            self._bounding_rect = QRectF(x, y, car.length, car_w)
        else:
            x = lane_offset + center_offset
            y = car.position_on_lane
            self._bounding_rect = QRectF(x, y, car_w, car.length)

        self._shape = QPainterPath()
        self._shape.addRect(self._bounding_rect)

        # Set color from car data or use default
        try:
            self._color = QColor(car.color)
        except (ValueError, TypeError):
            self._color = COLORS.CAR_DEFAULT

        self._calculate_reserved_corners()

    def _calculate_reserved_corners(self) -> None:
        """Calculate geometry for reserved intersection areas (triangles)."""
        self._reserved_shapes.clear()

        for crossing in self._data.reserved_crossings:
            h_road = self._road_accessor.get_road(crossing.lane_horizontal.road_name)
            v_road = self._road_accessor.get_road(crossing.lane_vertical.road_name)

            if not h_road or not v_road:
                continue

            lane_w = DIMENSION.LANE_WIDTH

            # Calculate intersection position
            h_top = h_road.position - ((h_road.forward_lanes + h_road.backward_lanes) * lane_w / 2)
            v_left = v_road.position - ((v_road.forward_lanes + v_road.backward_lanes) * lane_w / 2)

            x = v_left + (crossing.lane_vertical.lane_index * lane_w)
            y = h_top + (crossing.lane_horizontal.lane_index * lane_w)

            # Create triangle for reserved area
            p1 = QPointF(x, y)
            p2 = QPointF(x + lane_w, y)
            p3 = QPointF(x, y + lane_w)

            self._reserved_shapes.append(QPolygonF([p1, p2, p3]))