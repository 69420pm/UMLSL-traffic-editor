from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainterPath, QColor

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.view.view_models.entity_view_model import EntityViewModel


class CarViewModel(EntityViewModel[Car]):
    def __init__(self, car: Car, road_accessor):
        self._road_accessor = road_accessor
        super().__init__(car)

    def recalculate(self):
        # 1. Calculate Body Geometry (as discussed previously)
        # Using self._data (which is the Car entity)
        # ... math logic ...

        # 2. Update the cached properties required by the parent class
        self._bounding_rect = QRectF(...)
        self._shape = QPainterPath()
        self._shape.addRect(self._bounding_rect)
        self._color = QColor(self._data.color)