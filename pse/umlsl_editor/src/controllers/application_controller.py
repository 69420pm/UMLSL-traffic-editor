"""
Facade controller that combines ViewController and CommandController.
Provides a unified interface for the application's controller layer.
"""

from pse.umlsl_editor.src.controllers.data_controller import DataController
from pse.umlsl_editor.src.controllers.event_controller import EventController
from pse.umlsl_editor.src.controllers.command_controller import CommandController
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.view.ui.traffic_canvas.traffic import TrafficView


class ApplicationController(EventController, CommandController, DataController):
    """
    Main application controller that delegates responsibilities to specialized controllers:
    - ViewController: Handles model-to-view synchronization
    - CommandController: Handles command execution and undo/redo
    """

    def __init__(self, traffic_snapshot_reader: TrafficSnapshot, view: TrafficView):
        """
        Initialize the application controller with its sub-controllers.

        Args:
            traffic_snapshot_reader: The model that holds traffic simulation data.
            view: The view that displays the traffic simulation.
        """
        EventController.__init__(self, traffic_snapshot_reader, view)
        CommandController.__init__(self, traffic_snapshot_reader)



