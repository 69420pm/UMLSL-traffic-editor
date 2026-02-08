from dataclasses import dataclass

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.road import RoadOrientation
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment


@dataclass
class SegmentInterval:
    """
    Represents a segment interval on the virtual lane of the car.
    """
    segment: Segment
    interval: Interval

    def get_global_interval(self, ts: TrafficSnapshotReader, speed: float):
        """
        The interval stored as a property in this class is purely relative to the segment and the car's driving direction.
        This function converts the interval to a global interval. That means adding the target coordinate of the
        segment's start position to the interval yields the interval with global coordinates. (Target means for horizontal
        lanes it is the x position, for vertical lanes it is the y position.)
        """

        if isinstance(self.segment, CrossingSegment):
            return self.interval

        else:
            road = ts.get_road_by_uid(self.segment.lane.road_uid)

            car_direction: Direction
            if road.orientation == RoadOrientation.HORIZONTAL:
                car_direction = Direction.LEFT if (speed < 0) else Direction.RIGHT
            else:
                car_direction = Direction.DOWN if (speed < 0) else Direction.UP
            if not self.segment.lane.is_forward():
                car_direction = car_direction.opposite

            if road.orientation == RoadOrientation.HORIZONTAL and car_direction in [Direction.UP,
                                                                                    Direction.DOWN] or road.orientation == RoadOrientation.VERTICAL and car_direction in [
                Direction.LEFT, Direction.RIGHT]:
                return self.interval

            interval: Interval
            if car_direction == Direction.LEFT:
                right_end_segment = self.segment.get_size(ts)[0]
                interval = Interval(right_end_segment - self.interval.end, right_end_segment - self.interval.start)
            elif car_direction == Direction.DOWN:
                upper_end_segment = self.segment.get_size(ts)[1]
                interval = Interval(upper_end_segment - self.interval.end, upper_end_segment - self.interval.start)
            else:
                interval = self.interval
            return interval

    def __str__(self):
        return f"{self.segment} {self.interval}"
