"""
Road view model for the UMLSL Traffic Editor.

Calculates geometry and style for rendering roads.
"""
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QPainterPath, QPen, QBrush

from pse.umlsl_editor.src.view.view_constants import COLORS, DIMENSION
from pse.umlsl_editor.src.view.view_models.entity_view_model import EntityViewModel
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation


class RoadViewModel(EntityViewModel[Road]):
    """
    View model for Road entities.

    Calculates asphalt bounds, center line, and lane divider paths.
    Also stores style information (colors, pens, brushes).
    """

    def __init__(self, road: Road):
        """
        Initialize the road view model.

        Args:
            road: The Road domain entity.
        """
        self._center_line = QPainterPath()
        self._dashed_lines = QPainterPath()
        self._center_pen = QPen()
        self._dashed_pen = QPen()
        self._asphalt_brush = QBrush()

        super().__init__(road)

    @property
    def center_line(self) -> QPainterPath:
        """Return the center line path (between forward/backward lanes)."""
        return self._center_line

    @property
    def dashed_lines(self) -> QPainterPath:
        """Return the lane divider paths."""
        return self._dashed_lines

    @property
    def center_pen(self) -> QPen:
        """Return the pen for drawing the center line."""
        return self._center_pen

    @property
    def dashed_pen(self) -> QPen:
        """Return the pen for drawing lane dividers."""
        return self._dashed_pen

    @property
    def asphalt_brush(self) -> QBrush:
        """Return the brush for filling the road surface."""
        return self._asphalt_brush

    def recalculate(self) -> None:
        """Recalculate geometry and styles based on current road data."""
        road = self._data
        scene_size = DIMENSION.SCENE_SIZE
        lane_width = DIMENSION.LANE_WIDTH

        # Calculate asphalt rectangle
        width_f = road.forward_lanes * lane_width
        width_b = road.backward_lanes * lane_width

        if road.orientation == RoadOrientation.HORIZONTAL:
            y_start = road.position - width_f
            rect = QRectF(-scene_size / 2, y_start, scene_size, width_f + width_b)
        else:
            x_start = road.position - width_b
            rect = QRectF(x_start, -scene_size / 2, width_f + width_b, scene_size)

        self._bounding_rect = rect
        self._shape = QPainterPath()
        self._shape.addRect(rect)

        # Calculate center line (solid)
        self._calculate_center_line(road, scene_size)

        # Calculate lane dividers (dashed)
        self._calculate_lane_dividers(road, scene_size, lane_width)

        # Set up styles
        self._setup_styles(lane_width)

    def _calculate_center_line(self, road: Road, scene_size: int) -> None:
        """Calculate the center line path between traffic directions."""
        if road.forward_lanes >= 1 and road.backward_lanes >= 1:
            self._center_line = QPainterPath()
            if road.orientation == RoadOrientation.HORIZONTAL:
                self._center_line.moveTo(-scene_size / 2, road.position)
                self._center_line.lineTo(scene_size / 2, road.position)
            else:
                self._center_line.moveTo(road.position, -scene_size / 2)
                self._center_line.lineTo(road.position, scene_size / 2)

    def _calculate_lane_dividers(self, road: Road, scene_size: int, lane_width: float) -> None:
        """Calculate the dashed lane divider paths."""
        self._dashed_lines = QPainterPath()

        def add_divider(offset: float) -> None:
            if road.orientation == RoadOrientation.HORIZONTAL:
                self._dashed_lines.moveTo(-scene_size / 2, offset)
                self._dashed_lines.lineTo(scene_size / 2, offset)
            else:
                self._dashed_lines.moveTo(offset, -scene_size / 2)
                self._dashed_lines.lineTo(offset, scene_size / 2)

        for i in range(1, road.forward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                add_divider(road.position - (i * lane_width))
            else:
                add_divider(road.position + (i * lane_width))

        for i in range(1, road.backward_lanes):
            if road.orientation == RoadOrientation.HORIZONTAL:
                add_divider(road.position + (i * lane_width))
            else:
                add_divider(road.position - (i * lane_width))

    def _setup_styles(self, lane_width: float) -> None:
        """Set up brushes and pens for rendering."""
        # Asphalt style
        self._asphalt_brush = QBrush(COLORS.LAYER)

        # Center line style
        self._center_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._center_pen.setCosmetic(False)

        # Dashed line style
        self._dashed_pen = QPen(COLORS.TEXT, DIMENSION.LINE_WIDTH_ROAD_DIVIDER)
        self._dashed_pen.setStyle(Qt.DashLine)
        pen_width = self._dashed_pen.widthF()
        self._dashed_pen.setDashPattern([4, 8])
        self._dashed_pen.setCosmetic(False)