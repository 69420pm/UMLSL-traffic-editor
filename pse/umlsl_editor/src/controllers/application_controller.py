"""
Facade controller that combines ViewController and CommandController.
Provides a unified interface for the application's controller layer.
"""

from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.controllers.event_controller import EventController
from pse.umlsl_editor.src.controllers.command_controller import CommandController
from pse.umlsl_editor.src.model.domain_models.selection_model import SelectionModel
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel
from pse.umlsl_editor.src.view.view_event_handler_impl import ViewEventHandlerImplementation
from pse.umlsl_editor.src.view.view_models import ViewModels


class ApplicationController:
    """
    Main application controller that delegates responsibilities to specialized controllers:
    - ViewController: Handles model-to-view synchronization
    - CommandController: Handles command execution and undo/redo
    """

    def __init__(self):
        """
        Initialize the application controller with its sub-controllers.
        """
        self.model_view = ViewModels(roads=None, cars=None, umlsl_queries=None)
        self.model_traffic_snapshot = TrafficSnapshotModel()
        self.model_settings = SettingsModel(render_safety_distance=True, render_coordinate_system=True, breaking_acceleration=8.0)
        self.model_umlsl_queries = UMLSLQueriesModel()
        self.model_selection = SelectionModel()

        self.view_event_handler = ViewEventHandlerImplementation(view_model=self.model_view)

        self.event_controller = EventController(traffic_snapshot=self.model_traffic_snapshot, view=self.view_event_handler, settings=self.model_settings, umlsl_queries=self.model_umlsl_queries, selection=self.model_selection)
        self.command_controller = CommandController(traffic_snapshot_reader=self.model_traffic_snapshot, traffic_snapshot_writer=self.model_traffic_snapshot, settings_model=self.model_settings, umlsl_queries_model=self.model_umlsl_queries )
        self.data_controller = DataController(traffic_snapshot_reader=self.model_traffic_snapshot)

    def set_traffic_snapshot(self, traffic_snapshot: TrafficSnapshotModel):
        """
        Update the traffic snapshot model for all sub-controllers.

        Args:
            traffic_snapshot: The new traffic snapshot model.
        """
        self.model_traffic_snapshot = traffic_snapshot

        self.event_controller = EventController(traffic_snapshot=self.model_traffic_snapshot, view=self.view_event_handler, settings=self.model_settings)
        self.command_controller = CommandController(traffic_snapshot_reader=self.model_traffic_snapshot, traffic_snapshot_writer=self.model_traffic_snapshot)
        self.data_controller = DataController(traffic_snapshot_reader=self.model_traffic_snapshot)

        # Re-initialize the view to reflect the new traffic snapshot
        self.view_event_handler.initialize_view()
