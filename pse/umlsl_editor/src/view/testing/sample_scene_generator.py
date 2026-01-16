# pse/umlsl_editor/tests/sample_scene_generator.py
from dataclasses import dataclass
from typing import Optional

from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane, LaneDirection
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.view.view_constants import DIMENSION


# A simple implementation of the RoadAccessor protocol for testing
class TestRoadAccessor:
    def __init__(self, roads: list[Road]):
        self._roads_map = {r.name: r for r in roads}

    def get_road(self, road_name: str) -> Optional[Road]:
        return self._roads_map.get(road_name)


def create_sample_scene():
    """
    Creates a cross intersection with one car turning.
    Returns: (road_accessor, car, crossing_segment)
    """

    # --- 1. Create Roads (The Cross Intersection) ---
    # Horizontal Road (East-West)
    road_h = Road.from_params(RoadParams(
        name="Main Street",
        orientation=RoadOrientation.HORIZONTAL,
        position=0.0,  # Centered on Y-axis
        forward_lanes=1,  # 1 Lane going Right
        backward_lanes=1  # 1 Lane going Left
    ))

    # Vertical Road (North-South)
    road_v = Road.from_params(RoadParams(
        name="2nd Avenue",
        orientation=RoadOrientation.VERTICAL,
        position=0.0,  # Centered on X-axis
        forward_lanes=1,  # 1 Lane going Down
        backward_lanes=1  # 1 Lane going Up
    ))

    road_accessor = TestRoadAccessor([road_h, road_v])

    # --- 2. Create the "Crossing Segment" (The Corner) ---
    # Represents the intersection of Main St (Lane 0) and 2nd Ave (Lane 0)
    # This is the "Box" where the turn happens
    crossing = CrossingSegment(
        lane_horizontal=Lane(
            road_name=road_h.name,
            lane_index=0,
            lane_direction=LaneDirection.FORWARD
        ),
        lane_vertical=Lane(
            road_name=road_v.name,
            lane_index=0,
            lane_direction=LaneDirection.FORWARD
        )
    )

    # --- 3. Create a Car approaching the corner ---
    car = Car.from_params(CarParams(
        name="Red Turner",
        # Start on Main Street, 50 meters before the center
        lane=Lane(road_h.name, 0, LaneDirection.FORWARD),
        position_on_lane=-50.0,
        color="#FF0000",
        velocity=5.0,
        length=4.5,
        transition=0.0,
        next_turn=None,
        acceleration=0.0
    ))

    # IMPORTANT: Manually assign the reserved crossing to simulate
    # that the car is planning to turn or occupies that space.
    # In a real simulation, the backend logic would calculate this.
    car.reserved_crossings.append(crossing)

    return road_accessor, car, crossing