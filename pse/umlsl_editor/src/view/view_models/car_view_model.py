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

    def __init__(self, car: Car):
        """
        Initialize the car view model.

        Args:
            car: The Car domain entity.
            road_accessor: Object providing road lookup by name.
        """
        pass
