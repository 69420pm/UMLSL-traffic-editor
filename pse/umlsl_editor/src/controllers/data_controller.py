from typing import TYPE_CHECKING

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection

if TYPE_CHECKING:
    from pse.umlsl_editor.src.model.entities.car import Car
    from pse.umlsl_editor.src.model.entities.road import Road


class DataController:
    """Controller for providing data from the model to the view layer. It doesn't update anything automatic.
    It only serves data when requested."""

    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader):
        """
        Initialize the data controller.

        Args:
            traffic_snapshot_reader: The model that holds traffic simulation data.
        """
        self._traffic_snapshot_reader = traffic_snapshot_reader

    def get_all_cars(self) -> list["Car"]:
        return self._traffic_snapshot_reader.get_cars()

    def get_all_roads(self) -> dict[str, "Road"]:
        return self._traffic_snapshot_reader.get_roads()

    def get_breaking_acceleration(self) -> float:
        """Returns state of the breaking acceleration setting for the cars."""
        raise NotImplementedError

    def should_render_coordinate_system(self) -> bool:
        """Returns true if coordinate system is rendered."""
        raise NotImplementedError

    def should_render_safety_distance(self) -> bool:
        """Returns true if safety distance is rendered."""
        raise NotImplementedError

    def get_road_by_uid(self, uid: str) -> "Road":
        """Returns the road with the given uid."""
        return self._traffic_snapshot_reader.get_road_by_uid(uid)

    def get_valid_turn_intent_lanes(self, car_position: float, car_speed: float, car_lane: Lane, car_length: float,
                                    turn_direction: TurnDirection) -> list[Lane]:
        return self._traffic_snapshot_reader.get_valid_turn_intent_lanes(car_position, car_speed, car_lane, car_length,
                                                                         turn_direction)
