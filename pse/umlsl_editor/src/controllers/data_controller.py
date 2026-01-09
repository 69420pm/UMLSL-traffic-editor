from pse.umlsl_editor.src.core.entities.car import Car
from pse.umlsl_editor.src.core.entities.road import Road
from pse.umlsl_editor.src.core.traffic_snapshot_reader import TrafficSnapshotReader


class DataController:
    """Controller for providing data from the model to the view layer. It doesn't update anything automatic.
    It only serves data when requested."""

    def __init__(self, traffic_snapshot_reader: TrafficSnapshotReader):
        """
        Initialize the data controller.

        Args:
            traffic_snapshot_reader: The model that holds traffic simulation data.
        """
        self.traffic_snapshot_reader = traffic_snapshot_reader

    def get_all_cars(self) -> list[Car]:
        """Return all cars from the traffic snapshot."""
        raise NotImplementedError

    def get_all_roads(self) -> list[Road]:
        """Return all roads from the traffic snapshot."""
        raise NotImplementedError

    def get_breaking_acceleration(self) -> float:
        """Returns state of the breaking acceleration setting for the cars."""
        raise NotImplementedError

    def should_render_coordinate_system(self) -> bool:
        """Returns true if coordinate system is rendered."""
        raise NotImplementedError

    def should_render_safety_distance(self) -> bool:
        """Returns true if safety distance is rendered."""
        raise NotImplementedError