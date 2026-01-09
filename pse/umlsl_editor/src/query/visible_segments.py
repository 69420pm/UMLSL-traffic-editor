from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import Segment
from pse.umlsl_editor.src.query.ast.ast import View
from pse.umlsl_editor.src.query.interval import Interval


class SegmentView:
    def __init__(self, segment: Segment, space_interval: Interval):
        self.segment = segment
        self.space_interval = space_interval


class VisibleSegment:
    def __init__(self):
        pass


    def compute_visible_segments(self, view: View, car: Car) -> list[SegmentView]:
        # todo: extract visible lanes based on the space_interval and call the other method
        pass

    def compute_visible_segments_virtual_views(self, virtual_view: list[Segment], car: Car) -> list[SegmentView]:
        # todo: Algorithm 2 from paper
        pass

    # The sensor computes the size of the given car (depending on this view)
    def sensor_size(self, car: Car):
        return car.length
