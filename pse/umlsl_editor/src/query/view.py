from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Path
from pse.umlsl_editor.src.model.interval import Interval


class View:
    def __init__(self, seq_lanes: list[Path], space_interval: Interval, car: Car):
        self.seq_lanes = seq_lanes
        self.space_interval = space_interval
        self.car = car
