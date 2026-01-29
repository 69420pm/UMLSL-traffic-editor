"""
Sample scene generator for the UMLSL Traffic Editor.

Provides utilities for creating test traffic scenarios.
"""
from pse.umlsl_editor.src.controllers import ApplicationController
from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.car import CarParams, Car
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams, LaneDirection
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent, TurnDirection
from pse.umlsl_editor.src.view.view_event_handler_impl import ViewEventHandlerImplementation
from pse.umlsl_editor.src.view.view_models import ViewModels

# Horizontal Road (East-West)
r1 = Road.from_params(RoadParams(
    name="R1",
    orientation=RoadOrientation.HORIZONTAL,
    position=2.0,
    forward_lanes=0,
    backward_lanes=1
))

# Second Horizontal Road
r2 = Road.from_params(RoadParams(
    name="R2",
    orientation=RoadOrientation.HORIZONTAL,
    position=-3.0,
    forward_lanes=1,
    backward_lanes=2
))

# Vertical Road (North-South)
r3 = Road.from_params(RoadParams(
    name="R3",
    orientation=RoadOrientation.VERTICAL,
    position=-2.0,
    forward_lanes=2,
    backward_lanes=4
))

# Vertical Road (North-South)
r4 = Road.from_params(RoadParams(
    name="R4",
    orientation=RoadOrientation.VERTICAL,
    position=5.0,
    forward_lanes=1,
    backward_lanes=1
))

l1 = Lane(road_uid=r2.uid, lane_index=0, lane_direction=LaneDirection.BACKWARD)
l2 = Lane(road_uid=r3.uid, lane_index=0, lane_direction=LaneDirection.FORWARD)
l3 = Lane(road_uid=r1.uid, lane_index=0, lane_direction=LaneDirection.FORWARD)

c1 = Car.from_params(CarParams(
    name="C1",
    lane=l1,
    color="#eb34d8",
    position_on_lane=-5.0,
    transition=0.0,
    speed=10.0,
    length=1.5,
    next_turn=None,
    acceleration=10.0,
))

c2 = Car.from_params(CarParams(
    name="C2",
    lane=l2,
    color="#34eb43",
    position_on_lane=5.0,
    transition=0.0,
    speed=10.0,
    length=1.5,
    next_turn=TurnIntent(direction=TurnDirection.LEFT, target_lane=l1),
    acceleration=10.0,
))

c3 = Car.from_params(CarParams(
    name="C3",
    lane=l3,
    color="#34d5eb",
    position_on_lane=0.0,
    transition=0.0,
    speed=10.0,
    length=1.5,
    next_turn=TurnIntent(direction=TurnDirection.LEFT, target_lane=l1),
    acceleration=10.0,
))

class SampleTrafficSnapshotReader(TrafficSnapshotReader):
    def __init__(self):
        pass


    def get_cars_on_road(self, road: Road) -> list[Car]:
        pass

    def get_cars(self) -> list[Car]:
        return [c1, c2, c3]

    def get_roads(self) -> list[Road]:
        return [r1, r2, r3, r4]

    def get_cars_in_rectangle(
            self, x_min: float, y_min: float, x_max: float, y_max: float
    ) -> list[Car]:
        """
        Returns a list of cars that are located within the specified rectangular area.
        """
        pass

    def get_roads_in_rectangle(
            self, x_min: float, y_min: float, x_max: float, y_max: float
    ) -> list[Road]:
        """
        Returns a list of roads that are located within the specified rectangular area.
        """
        pass

    def get_max_velocity(self) -> float:
        """
        Returns the maximum velocity of all cars in the snapshot.
        """
        pass

    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool:
        """
        Validates if the specified lane index and direction exist on the given road.

        Args:
            road: The road to validate against.
            lane_index: The index of the lane to validate.
            lane_direction: The direction of the lane to validate ('fn' for forward, 'bn' for backward).

        Returns:
            True if the lane index and direction are valid for the road, False otherwise.
        """
        pass

class TestApplicationController(ApplicationController):
    def __init__(self):
        self.data_controller = TestDataController()
        self.view_event_handler = ViewEventHandlerImplementation(self.data_controller.get_view_models())

class TestDataController(DataController):
    def __init__(self):
        traffic_snapshot_reader = SampleTrafficSnapshotReader()
        super().__init__(traffic_snapshot_reader)

        self._view_models = ViewModels(roads = traffic_snapshot_reader.get_roads(), cars= traffic_snapshot_reader.get_cars(), umlsl_queries=[])
        self._traffic_snapshot_reader = traffic_snapshot_reader

    def get_view_models(self) -> ViewModels:
        """Return the view models."""
        return self._view_models

    def get_all_cars(self) -> list[Car]:
        """Return all cars from the traffic snapshot."""
        return self._traffic_snapshot_reader.get_cars()

    def get_all_roads(self) -> list[Road]:
        """Return all roads from the traffic snapshot."""
        return self._traffic_snapshot_reader.get_roads()

    def get_breaking_acceleration(self) -> float:
        return 8.0

    def should_render_coordinate_system(self) -> bool:
        return True

    def should_render_safety_distance(self) -> bool:
        return True

