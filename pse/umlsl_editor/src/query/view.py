from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import VirtualLane, Segment
from pse.umlsl_editor.src.model.interval import Interval


class View:
    def __init__(self, virtual_lanes: list[VirtualLane], horizon: Interval, car: 'Car'):
        self.virtual_lanes = virtual_lanes
        self.horizon = horizon
        self.car = car
