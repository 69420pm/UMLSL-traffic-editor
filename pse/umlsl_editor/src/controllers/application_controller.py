"""
Facade controller that combines ViewController and CommandController.
Provides a unified interface for the application's controller layer.
"""

from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.controllers.event_controller import EventController
from pse.umlsl_editor.src.controllers.command_controller import CommandController
from pse.umlsl_editor.src.model.view_models.settings import Settings
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.view.traffic_view import TrafficView


class ApplicationController:
    """
    Main application controller that delegates responsibilities to specialized controllers:
    - ViewController: Handles model-to-view synchronization
    - CommandController: Handles command execution and undo/redo
    """

    def __init__(self, traffic_snapshot: TrafficSnapshot, view: TrafficView, settings: Settings):
        """
        Initialize the application controller with its sub-controllers.

        Args:
            traffic_snapshot: The model that holds traffic simulation data.
            view: The view that displays the traffic simulation.
        """
        self.traffic_snapshot = traffic_snapshot
        self.view = view
        self.settings = settings
        self.event_controller = EventController(traffic_snapshot=traffic_snapshot, view=view, settings=settings)
        self.command_controller = CommandController(traffic_snapshot_reader=traffic_snapshot, traffic_snapshot_writer=traffic_snapshot)
        self.data_controller = DataController(traffic_snapshot_reader=traffic_snapshot)

    def set_traffic_snapshot(self, traffic_snapshot: TrafficSnapshot):
        """
        Update the traffic snapshot model for all sub-controllers.

        Args:
            traffic_snapshot: The new traffic snapshot model.
        """
        self.traffic_snapshot = traffic_snapshot

        self.event_controller = EventController(traffic_snapshot=self.traffic_snapshot, view=self.view, settings=self.settings)
        self.command_controller = CommandController(traffic_snapshot_reader=self.traffic_snapshot, traffic_snapshot_writer=self.traffic_snapshot)
        self.data_controller = DataController(traffic_snapshot_reader=self.traffic_snapshot)

        # Re-initialize the view to reflect the new traffic snapshot
        self.view.initialize_view()
