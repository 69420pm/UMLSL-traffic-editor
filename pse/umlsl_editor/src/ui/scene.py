from typing import Dict

from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot


class SceneManager:
    """Intermediary between Data and Visual Items."""
    def __init__(self, canvas: 'TrafficVisualEditor'):
        self.canvas = canvas
        self.road_items: Dict[str, 'RoadGraphicsItem'] = {}
        self.car_items: Dict[str, 'CarGraphicsItem'] = {}

    def update_scene(self, snapshot: TrafficSnapshot):
        pass
