from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import VirtualLaneNew


class View:
    def __init__(self, virtual_lanes: list[VirtualLaneNew], horizon: Interval, car: 'Car',
                 intersecting_cars: dict[str, dict[Segment, Interval]],
                 reserved_segments: dict[str, dict[Segment, Interval]],
                 claimed_segments: dict[str, dict[Segment, Interval]],
                 ):
        self.virtual_lanes = virtual_lanes
        self.horizon = horizon
        # todo: rename to ego
        self.car = car
        self.cars_in_view = [car for car, intervals in intersecting_cars.items() if len(intervals) > 0]
        self.intersecting_cars = intersecting_cars
        self.reserved_segments = reserved_segments
        self.claimed_segments = claimed_segments

    def chop_horizontally(self, split: float) -> tuple['View', 'View']:
        left_horizon = Interval(self.horizon.start, split)
        left_view = self._construct_view(left_horizon, self.virtual_lanes)

        right_horizon = Interval(split, self.horizon.end)
        right_view = self._construct_view(right_horizon, self.virtual_lanes)

        return left_view, right_view

    def chop_vertically(self, split: int) -> tuple['View', 'View']:
        lower_lanes = self.virtual_lanes[:split]  # take all lanes whose index is < split_index
        lower_view = self._construct_view(self.horizon, lower_lanes)

        upper_lanes = self.virtual_lanes[split:]
        upper_view = self._construct_view(self.horizon, upper_lanes)

        return lower_view, upper_view

    def _construct_view(self, horizon: Interval, lanes: list[VirtualLaneNew]) -> 'View':
        segments_in_view: list[Segment] = []
        new_virtual_lanes: list[VirtualLaneNew] = []

        for virtual_lane in lanes:
            new_virtual_lane = []

            for segment_interval in virtual_lane.segment_intervals:
                # only take those segments that are in the horizon
                if horizon.intersects(segment_interval.interval):
                    segments_in_view.append(segment_interval.segment)
                    new_virtual_lane.append(segment_interval)

            new_virtual_lanes.append(VirtualLaneNew(new_virtual_lane, []))

        # only consider cars that intersect with the horizon
        new_intersecting_cars: dict[str, dict[Segment, Interval]] = dict()
        for intersecting_car in self.intersecting_cars:
            occupied_segment_interval: dict[Segment, Interval] = self.intersecting_cars[intersecting_car]
            any_intersects = any(
                occupied_segment in segments_in_view and occupied_interval.intersects(horizon)
                for occupied_segment, occupied_interval in occupied_segment_interval.items()
            )
            if any_intersects:
                new_intersecting_cars[intersecting_car] = occupied_segment_interval

        # only consider reserved segments that intersect with the horizon
        new_reserved_segments: dict[str, dict[Segment, Interval]] = dict()
        for car in self.reserved_segments:
            reserved_segments: dict[Segment, Interval] = self.reserved_segments[car]

            new_reserved_car_segments: dict[Segment, Interval] = dict()
            for segment, interval in reserved_segments.items():
                if segment in segments_in_view and horizon.intersects(interval):
                    new_reserved_car_segments[segment] = interval

            new_reserved_segments[car] = new_reserved_car_segments

        # only consider claimed segments that intersect with the horizon
        new_claimed_segments: dict[str, dict[Segment, Interval]] = dict()
        for car in self.claimed_segments:
            claimed_segments: dict[Segment, Interval] = self.reserved_segments[car]

            new_claimed_car_segments: dict[Segment, Interval] = dict()
            for segment, interval in claimed_segments.items():
                if segment in segments_in_view and horizon.intersects(interval):
                    new_claimed_car_segments[segment] = interval

            new_claimed_segments[car] = claimed_segments

        return View(new_virtual_lanes, horizon, self.car, new_intersecting_cars, new_reserved_segments, new_claimed_segments)


