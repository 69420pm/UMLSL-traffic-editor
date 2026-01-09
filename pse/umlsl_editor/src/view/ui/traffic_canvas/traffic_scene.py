from PySide6.QtWidgets import QGraphicsScene

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import (
    CrossingSegment,
)


class TrafficScene(QGraphicsScene):
    """
    A custom QGraphicsScene for rendering the traffic simulation.
    Manages the graphical representation of cars, roads, and crossing segments.

    Designer-based structure:
    - This scene is intended to be paired with a QGraphicsView (e.g., a promoted
      TrafficCanvasView) defined in a Qt Designer .ui file.
    - The .ui should contain a QGraphicsView in the traffic_canvas area that is promoted
      to TrafficCanvasView, with a stable objectName (e.g., 'trafficView').
    - A UI binder (e.g., MainWindowUiBinder) should find that view by objectName
      and set its scene to an instance of this TrafficScene.

    Separation of concerns:
    - TrafficScene: owns and manages QGraphicsItems (roads, cars, crossings).
    - TrafficCanvasView: handles interaction (pan, zoom) and transformation.
    - Designer .ui: defines layout and widget placement; objectNames enable binders
      to locate and wire the scene and view at runtime.
    - Controllers: connect model signals to view methods; rendering logic and item
      updates are invoked via the TrafficView interface, not from within .ui binders.

    Notes:
    - Method bodies for adding/updating/removing items are kept as structure-only
      placeholders to align with the requirement of not implementing methods.
    - Coordinate system rendering, safety distance, and other overlays should be
      toggled via settings and handled by the view/scene when those methods are
      implemented later.
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        # Store mappings from data objects to graphics items
        self._car_items = {}  # Map car name to QGraphicsItem
        self._road_items = {}  # Map road name to QGraphicsItem
        self._crossing_items = {}  # Map crossing segment to QGraphicsItem

        # Set scene background
        # self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))

    def add_car_item(self, car_data: Car) -> None:
        """
        Creates a graphical item for a new car and adds it to the scene.
        """
        # if car_data.name in self._car_items:
        #     return
        #
        # # Create a simple rectangle to represent the car
        # # Position calculation would depend on road geometry
        # car_item = QGraphicsRectItem(0, 0, car_data.length * 10, 20)
        # car_item.setBrush(QBrush(QColor(car_data.color)))
        # car_item.setPen(QPen(Qt.GlobalColor.black, 1))
        #
        # # TODO: Calculate actual position based on assigned_road, lane_index, position_on_lane
        # # For now, place it at a simple position
        # car_item.setPos(car_data.position_on_lane * 10, car_data.lane_index * 30)
        #
        # self.addItem(car_item)
        # self._car_items[car_data.name] = car_item

    def remove_car_item(self, car_data: Car) -> None:
        """
        Removes the graphical item corresponding to the given car from the scene.
        """
        # if car_data.name not in self._car_items:
        #     return
        #
        # car_item = self._car_items[car_data.name]
        # self.removeItem(car_item)
        # del self._car_items[car_data.name]

    def update_car_item(self, car_data: Car) -> None:
        """
        Updates the properties (position, color, etc.) of an existing car item.
        """
        # if car_data.name not in self._car_items:
        #     return
        #
        # car_item = self._car_items[car_data.name]
        #
        # # Update position
        # car_item.setPos(car_data.position_on_lane * 10, car_data.lane_index * 30)
        #
        # # Update color
        # car_item.setBrush(QBrush(QColor(car_data.color)))

    def add_road_item(self, road_data: Road) -> None:
        """
        Creates a graphical item for a new road and adds it to the scene.
        """
        # if road_data.name in self._road_items:
        #     return
        #
        # # Create a simple line/rectangle to represent the road
        # # Road width based on number of lanes
        # total_lanes = road_data.forward_lanes + road_data.backward_lanes
        # road_width = total_lanes * 30
        #
        # # Draw road based on orientation
        # # Roads are infinite lines, so we'll draw a large segment for visibility
        # road_length = 2000  # Large enough for typical viewport
        #
        # if road_data.orientation == RoadOrientation.HORIZONTAL:
        #     # Horizontal road: position is Y-coordinate, extend along X-axis
        #     road_item = QGraphicsRectItem(
        #         -road_length / 2,
        #         road_data.position - road_width / 2,
        #         road_length,
        #         road_width
        #     )
        # else:  # VERTICAL
        #     # Vertical road: position is X-coordinate, extend along Y-axis
        #     road_item = QGraphicsRectItem(
        #         road_data.position - road_width / 2,
        #         -road_length / 2,
        #         road_width,
        #         road_length
        #     )
        #
        # road_item.setBrush(QBrush(QColor(80, 80, 80)))
        # road_item.setPen(QPen(Qt.GlobalColor.white, 2))
        #
        # self.addItem(road_item)
        # self._road_items[road_data.name] = road_item

    def remove_road_item(self, road_data: Road) -> None:
        """
        Removes the graphical item corresponding to the given road from the scene.
        """
        # if road_data.name not in self._road_items:
        #     return
        #
        # road_item = self._road_items[road_data.name]
        # self.removeItem(road_item)
        # del self._road_items[road_data.name]

    def update_road_item(self, road_data: Road) -> None:
        """
        Updates the properties (geometry, lanes, etc.) of an existing road item.
        """
        # if road_data.name not in self._road_items:
        #     return
        #
        # # For simplicity, remove and re-add the road item
        # self.remove_road_item(road_data)
        # self.add_road_item(road_data)

    def add_crossing_segment_item(self, crossing: CrossingSegment) -> None:
        """
        Creates a graphical item for a crossing segment and adds it to the scene.
        """
        # crossing_id = id(crossing)
        # if crossing_id in self._crossing_items:
        #     return
        #
        # # Draw crossing as a circle/ellipse
        # crossing_item = QGraphicsEllipseItem(
        #     crossing.position.x - 25,
        #     crossing.position.y - 25,
        #     50, 50
        # )
        # crossing_item.setBrush(QBrush(QColor(200, 150, 100, 180)))
        # crossing_item.setPen(QPen(Qt.GlobalColor.darkGray, 2))
        #
        # self.addItem(crossing_item)
        # self._crossing_items[crossing_id] = crossing_item

    def remove_crossing_segment_item(self, crossing: CrossingSegment) -> None:
        """
        Removes the graphical item for a crossing segment.
        """
        # crossing_id = id(crossing)
        # if crossing_id not in self._crossing_items:
        #     return
        #
        # crossing_item = self._crossing_items[crossing_id]
        # self.removeItem(crossing_item)
        # del self._crossing_items[crossing_id]

    def update_crossing_segment_item(self, crossing: CrossingSegment) -> None:
        """
        Updates the graphical item for a crossing segment.
        """
        # crossing_id = id(crossing)
        # if crossing_id not in self._crossing_items:
        #     return
        #
        # # For simplicity, remove and re-add
        # self.remove_crossing_segment_item(crossing)
        # self.add_crossing_segment_item(crossing)
