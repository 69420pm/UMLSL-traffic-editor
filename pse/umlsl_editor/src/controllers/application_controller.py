"""
Facade controller that combines ViewController and CommandController.
Provides a unified interface for the application's controller layer.
"""

from typing import Optional

from pse.umlsl_editor.src.controllers.view_controller import ViewController
from pse.umlsl_editor.src.controllers.command_controller import CommandController
from pse.umlsl_editor.src.core.dataclasses.road import Road, LaneDirection
from pse.umlsl_editor.src.core.dataclasses.turn_intent import TurnIntent
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.view.traffic_view import TrafficView


class ApplicationController(ViewController, CommandController):
    """
    Main application controller that delegates responsibilities to specialized controllers:
    - ViewController: Handles model-to-view synchronization
    - CommandController: Handles command execution and undo/redo
    """

    def __init__(self, traffic_snapshot: TrafficSnapshot, view: TrafficView):
        """
        Initialize the application controller with its sub-controllers.

        Args:
            traffic_snapshot: The model that holds traffic simulation data.
            view: The view that displays the traffic simulation.
        """
        ViewController.__init__(self, traffic_snapshot, view)
        CommandController.__init__(self, traffic_snapshot)



