"""Controller responsible for synchronizing the model state to the view layer."""

from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.view.traffic_view import TrafficView


class ViewController:
    """
    Connects TrafficSnapshot model signals directly to TrafficView methods.
    Handles all model-to-view synchronization without intermediate logic.
    """

    def __init__(self, traffic_snapshot: TrafficSnapshot, view: TrafficView):
        """
        Initialize the view controller.

        Args:
            traffic_snapshot: The model that emits signals when data changes.
            view: The view that displays the traffic simulation.
        """
        self.traffic_snapshot = traffic_snapshot
        self.view = view
        self._setup_event_listeners()

    def _setup_event_listeners(self) -> None:
        """
        Connects TrafficSnapshot signals directly to TrafficView methods.
        This eliminates intermediate handler methods for simple pass-through cases.
        """
        # Connect Car signals directly to view methods
        self.traffic_snapshot.car_added.connect(self.view.add_car_view)
        self.traffic_snapshot.car_removed.connect(self.view.remove_car_view)
        self.traffic_snapshot.car_updated.connect(self.view.update_car_view)

        # Connect Road signals directly to view methods
        self.traffic_snapshot.road_added.connect(self.view.add_road_view)
        self.traffic_snapshot.road_removed.connect(self.view.remove_road_view)
        self.traffic_snapshot.road_updated.connect(self.view.update_road_view)

        # Connect Crossing Segment signals directly to view methods
        self.traffic_snapshot.crossing_segment_added.connect(self.view.add_crossing_segment_view)
        self.traffic_snapshot.crossing_segment_removed.connect(self.view.remove_crossing_segment_view)
        self.traffic_snapshot.crossing_segment_updated.connect(self.view.update_crossing_segment_view)

        # Connect UMLSL Query signals directly to view methods
        self.traffic_snapshot.umlsl_query_added.connect(self.view.add_query_view)
        self.traffic_snapshot.umlsl_query_removed.connect(self.view.remove_query_view)
        self.traffic_snapshot.umlsl_query_updated.connect(self.view.update_query_view)

