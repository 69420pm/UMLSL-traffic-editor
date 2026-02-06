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

    def get_all_cars(self) -> dict[str, "Car"]:
        return self._traffic_snapshot_reader.get_cars()

    def get_all_roads(self) -> dict[str, "Road"]:
        return self._traffic_snapshot_reader.get_roads()

    def get_road_by_uid(self, uid: str) -> "Road":
        """Returns the road with the given uid."""
        return self._traffic_snapshot_reader.get_road_by_uid(uid)
