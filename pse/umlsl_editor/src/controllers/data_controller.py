from typing import TYPE_CHECKING

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader

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
