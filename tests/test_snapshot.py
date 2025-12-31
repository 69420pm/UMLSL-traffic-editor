from pse.umlsl_editor.src.core.dataclasses.car import Car, CarParams
from pse.umlsl_editor.src.core.dataclasses.road import Road, RoadParams, RoadOrientation, LaneDirection
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot


def create_test_snapshot() -> TrafficSnapshot:
    road1 = Road.from_params(
        RoadParams(
            name="R1",
            orientation=RoadOrientation.HORIZONTAL,
            position=1.0,
            forward_lanes=1,
            backward_lanes=0
        )
    )
    road2 = Road.from_params(
        RoadParams(
            name="R2",
            orientation=RoadOrientation.VERTICAL,
            position=5.0,
            forward_lanes=1,
            backward_lanes=0
        )
    )

    roads = [road1, road2]
    cars = [
        Car.from_params(
            CarParams(
                name="C1",
                assigned_road=road1,
                lane_index=0,
                lane_direction=LaneDirection.FORWARD,
                color="red",
                position_on_lane=0.0,
                transition=0.0,
                velocity=1.0,
                length=2.0,
                next_turn=None
            )
        ),
        Car.from_params(
            CarParams(
                name="C2",
                assigned_road=road2,
                lane_index=0,
                lane_direction=LaneDirection.FORWARD,
                color="blue",
                position_on_lane=0.0,
                transition=0.0,
                velocity=1.0,
                length=2.0,
                next_turn=None
            )
        )
    ]

    roads_by_name: dict[str, Road] = {road.name: road for road in roads}
    cars_by_name: dict[str, Car] = {car.name: car for car in cars}

    return TrafficSnapshot(roads_by_name, cars_by_name)
