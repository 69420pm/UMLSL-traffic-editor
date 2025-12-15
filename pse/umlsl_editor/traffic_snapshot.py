from typing import Dict, List

from pse.umlsl_editor.car import Car
from pse.umlsl_editor.road import Road
from pse.umlsl_editor.ui.settings import SimulationSettings


class TrafficSnapshot:
    """Root data object (The 'Document')."""
    def __init__(self):
        self.roads: Dict[str, Road] = {}
        self.cars: Dict[str, Car] = {}
        self.queries: List['UMLSLQuery'] = []
        self.settings: SimulationSettings = SimulationSettings()