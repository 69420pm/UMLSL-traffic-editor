from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import Path
from pse.umlsl_editor.src.query.interval import Interval


class View:
    def __init__(self, seq_lanes: list[Path], space_interval: Interval, car: Car):
        self.seq_lanes = seq_lanes
        self.space_interval = space_interval
        self.car = car
