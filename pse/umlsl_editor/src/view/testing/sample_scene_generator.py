"""
Sample scene generator for the UMLSL Traffic Editor.

Provides utilities for creating test traffic scenarios.
"""
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane, LaneDirection


def create_sample_scene() -> list:
    """
    Create a sample cross intersection with roads.

    Returns:
        List of Road entities forming a cross intersection.
    """
    # Horizontal Road (East-West)
    r1 = Road.from_params(RoadParams(
        name="R1",
        orientation=RoadOrientation.HORIZONTAL,
        position=5.0,
        forward_lanes=4,
        backward_lanes=1
    ))

    # Vertical Road (North-South)
    r3 = Road.from_params(RoadParams(
        name="R3",
        orientation=RoadOrientation.VERTICAL,
        position=0.0,
        forward_lanes=3,
        backward_lanes=5
    ))

    # Second Horizontal Road
    r2 = Road.from_params(RoadParams(
        name="R2",
        orientation=RoadOrientation.HORIZONTAL,
        position=10.0,
        forward_lanes=1,
        backward_lanes=4
    ))

    return [r1, r2, r3]