from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_interval import SegmentInterval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.query.ast.ast import View
from pse.umlsl_editor.src.query.interval import Interval


class VisibleSegment:
    def __init__(self):
        pass


    def compute_visible_segments(self, view: View, car: Car) -> list[SegmentInterval]:
        # todo: extract visible lanes based on the space_interval and call the other method
        pass

    # The sensor computes the size of the given car (depending on this view)
    def get_sensor_size(self, view: View, car: Car):
        return car.length
