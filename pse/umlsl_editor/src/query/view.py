from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import VirtualLane
from pse.umlsl_editor.src.model.interval import Interval


class View:
    def __init__(self, virtual_lanes: list[VirtualLane], space_interval: Interval, car: Car):
        self.virtual_lanes = virtual_lanes
        self.space_interval = space_interval
        self.car = car
