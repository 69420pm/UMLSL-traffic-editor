from dataclasses import dataclass

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import VirtualLane

@dataclass(frozen=True)
class CoordinateTranslation:
    visible: dict[str, dict[Segment, Interval]]
    reserved: dict[str, dict[Segment, Interval]]
    claimed: dict[str, dict[Segment, Interval]]

def translate_into_ego_coordinates(
        ts: TrafficSnapshotModel, ego: Car, horizontal_horizon: Interval, virtual_lanes: list[VirtualLane]
) -> CoordinateTranslation :
    def translate_coordinate_system(func) -> dict[str, dict[Segment, Interval]]:
        translated: dict[str, dict[Segment, Interval]] = {}
        for traffic_snapshot_car in ts.get_car_list():
            translated[traffic_snapshot_car.uid] = ego.environment.translate_interval_coordinates(
                virtual_lanes,
                horizontal_horizon,
                func(traffic_snapshot_car),
                traffic_snapshot_car,
                ts
            )
        return translated

    # translate physical, reserved and claimed intervals of every car into the coordinate system of ego
    intersecting_cars: dict[str, dict[Segment, Interval]] = translate_coordinate_system(
        lambda c: c.environment.physical_segment_intervals)
    reserved_segments: dict[str, dict[Segment, Interval]] = translate_coordinate_system(
        lambda c: c.environment.reserved)
    claimed_segments: dict[str, dict[Segment, Interval]] = translate_coordinate_system(
        lambda c: c.environment.claimed
    )

    print("evaluating parallel virtual lane with horizon ", horizontal_horizon.start, horizontal_horizon.end)
    print("visible cars: ")
    for intersecting_car in intersecting_cars:
        print(">", ts.cars[intersecting_car].name, ":")
        for segment, interval in intersecting_cars[intersecting_car].items():
            print(f"  {ts.get_segment_info(segment.uid)}: {interval}")
    print("")
    print("reserved cars: ")
    for intersecting_car in reserved_segments:
        print(">", ts.cars[intersecting_car].name, ":")
        for segment, interval in reserved_segments[intersecting_car].items():
            print(f"  {ts.get_segment_info(segment.uid)}: {interval}")

    return CoordinateTranslation(intersecting_cars, reserved_segments, claimed_segments)
