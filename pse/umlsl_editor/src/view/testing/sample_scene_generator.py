"""
Sample scene generator for the UMLSL Traffic Editor.

Provides utilities for creating test traffic scenarios.
"""
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams


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



    return [r1, r2, r3, r4]