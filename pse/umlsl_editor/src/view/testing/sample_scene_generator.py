"""
Sample scene generator for the UMLSL Traffic Editor.

Provides utilities for creating test traffic scenarios.
"""
from pse.umlsl_editor.src.model.entities.car import CarParams, Car
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams, LaneDirection
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent, TurnDirection


def create_sample_scene():
    """
    Create a sample cross intersection with roads.

    Returns:
        List of Road entities forming a cross intersection.
    """
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
        backward_lanes=2
    ))

    # Vertical Road (North-South)
    r4 = Road.from_params(RoadParams(
        name="R4",
        orientation=RoadOrientation.VERTICAL,
        position=5.0,
        forward_lanes=1,
        backward_lanes=1
    ))

    l1 = Lane(road_uid=r1.uid, lane_index=0, lane_direction=LaneDirection.FORWARD)
    l2 = Lane(road_uid=r3.uid, lane_index=-1, lane_direction=LaneDirection.BACKWARD)

    c1 = Car.from_params(CarParams(
        name="C1",
        lane=l2,
        color="#1F2335",
        position_on_lane=10.0,
        transition=0.0,
        velocity=10.0,
        length=2.0,
        next_turn=TurnIntent(direction=TurnDirection.LEFT, target_lane=l1),
        acceleration=10.0,
    ))



    return [r1, r3], [c1]
