from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath, QColor

from pse.umlsl_editor.src.view.view_models.entity_view_model import EntityViewModel
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation


class RoadViewModel(EntityViewModel[Road]):
    def recalculate(self):
        road = self._data

        # 1. Calculate Road Geometry
        length = 2000
        width = (road.forward_lanes + road.backward_lanes) * 30

        if road.orientation == RoadOrientation.HORIZONTAL:
            rect = QRectF(-length / 2, road.position - width / 2, length, width)
        else:
            rect = QRectF(road.position - width / 2, -length / 2, width, length)

        self._bounding_rect = rect
        self._shape = QPainterPath()
        self._shape.addRect(rect)
        self._color = QColor(80, 80, 80)