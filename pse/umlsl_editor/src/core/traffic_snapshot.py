from typing import Dict, List

from pse.umlsl_editor.src.core.car import Car
from pse.umlsl_editor.src.core.road import Road
from pse.umlsl_editor.src.ui.settings import SimulationSettings


class TrafficSnapshot:
    """Root data object (The 'Document')."""
    def __init__(self):
        self.roads: Dict[str, Road] = {}
        self.cars: Dict[str, Car] = {}
        self.queries: List['UMLSLQuery'] = []
        self.settings: SimulationSettings = SimulationSettings()