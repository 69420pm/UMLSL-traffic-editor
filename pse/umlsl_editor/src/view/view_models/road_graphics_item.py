"""
Road graphics item for the UMLSL Traffic Editor.

Custom QGraphicsItem that renders roads with asphalt, center lines, and lane dividers.
"""
from PySide6.QtWidgets import QGraphicsItemGroup, QGraphicsRectItem, QGraphicsPathItem
from PySide6.QtCore import Qt

from pse.umlsl_editor.src.view.view_models.road_view_model import RoadViewModel


class RoadGraphicsItem(QGraphicsItemGroup):
    """
    Graphics item that renders a road based on a RoadViewModel.

    Contains:
        - Asphalt rectangle
        - Center line (solid)
        - Lane dividers (dashed)

    Lane labels are rendered in TrafficView's foreground for always-visible overlay.
    """

    def __init__(self, vm: RoadViewModel):
        """
        Initialize the road graphics item.

        Args:
            vm: The RoadViewModel containing geometry and style data.
        """
        super().__init__()

        # Create child items (created once, updated on changes)
        self._asphalt = QGraphicsRectItem(self)
        self._asphalt.setPen(Qt.NoPen)

        self._center_line = QGraphicsPathItem(self)
        self._dashed_lines = QGraphicsPathItem(self)

        # Add to group
        self.addToGroup(self._asphalt)
        self.addToGroup(self._center_line)
        self.addToGroup(self._dashed_lines)

        # Initial draw
        self.update_visuals(vm)

    def update_visuals(self, vm: RoadViewModel) -> None:
        """
        Apply geometry and style from the view model.

        Args:
            vm: The RoadViewModel with updated data.
        """
        self._asphalt.setRect(vm.bounding_rect)
        self._asphalt.setBrush(vm.asphalt_brush)

        self._center_line.setPath(vm.center_line)
        self._center_line.setPen(vm.center_pen)

        self._dashed_lines.setPath(vm.dashed_lines)
        self._dashed_lines.setPen(vm.dashed_pen)

