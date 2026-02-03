"""
Facade controller that combines ViewController and CommandController.
Provides a unified interface for the application's controller layer.
"""

from pse.umlsl_editor.src.controllers.command_controller import CommandController
from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.controllers.event_controller import EventController
from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
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
        self._model_view = ViewModels(self)
        self._model_traffic_snapshot = TrafficSnapshotModel()
        self._model_settings = SettingsModel(render_safety_distance=True, render_coordinate_system=True,
                                             breaking_acceleration=8.0)
        self._model_umlsl_queries = UMLSLQueriesModel()

        self.view_event_handler = ViewEventHandlerImplementation(view_model=self._model_view)

        self._model_view.connect_signals(self.view_event_handler)

        self.event_controller = EventController(traffic_snapshot=self._model_traffic_snapshot,
                                                view=self.view_event_handler, settings=self._model_settings,
                                                umlsl_queries=self._model_umlsl_queries)
        self.command_controller = CommandController(traffic_snapshot_reader=self._model_traffic_snapshot,
                                                    traffic_snapshot_writer=self._model_traffic_snapshot,
                                                    settings_model=self._model_settings,
                                                    umlsl_queries_model=self._model_umlsl_queries)
        self.data_controller = DataController(traffic_snapshot_reader=self._model_traffic_snapshot)

    def get_traffic_snapshot_reader(self) -> TrafficSnapshotReader:
        return self._model_traffic_snapshot

    def get_traffic_snapshot_writer(self) -> TrafficSnapshotWriter:
        return self._model_traffic_snapshot

    def set_traffic_snapshot(self, traffic_snapshot: TrafficSnapshotModel):
        """
        Update the traffic snapshot model for all sub-controllers.

        Args:
            traffic_snapshot: The new traffic snapshot model.
        """
        self._model_traffic_snapshot = traffic_snapshot
        # self._view_event_handler.initialize_view()
