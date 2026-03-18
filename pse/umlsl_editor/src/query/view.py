from typing import TypeVar, Generic, Callable

from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.virtual_lane import VirtualLaneNew

T = TypeVar('T')


class LazyEvaluator(Generic[T]):
    def __init__(self, data: T, on_update: Callable[[T], T]):
        self.data = data
        self.updated = False
        self.on_update = on_update

    def acquire_data(self) -> T:
        if not self.updated:
            self.data = self.on_update(self.data)
            self.updated = True
        return self.data


class View:
    def __init__(self, virtual_lanes: list[VirtualLaneNew], segments_in_view: list[Segment],
                 horizon: Interval, car: 'Car',
                 intersecting_cars: dict[str, dict[Segment, Interval]],
                 reserved_segments: dict[str, dict[Segment, Interval]],
                 claimed_segments: dict[str, dict[Segment, Interval]],
                 ):
        self.virtual_lanes = virtual_lanes
        self.segments_in_view = segments_in_view
        self.horizon = horizon
        # todo: rename to ego
        self.car = car

        self._lazy_intersecting_cars = LazyEvaluator(
            intersecting_cars,
            lambda old_cars: self._compute_intersecting_cars_in_view(old_cars)
        )
        self._lazy_reserved_segments = LazyEvaluator(
            reserved_segments,
            lambda old_reserved: self._compute_reserved_segments_in_view(old_reserved)
        )
        self._lazy_claimed_segments = LazyEvaluator(
            claimed_segments,
            lambda old_claimed: self._compute_claimed_segments_in_view(old_claimed)
        )

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

            if len(new_virtual_lane) > 0:
                new_virtual_lanes.append(VirtualLaneNew(new_virtual_lane, []))

        return View(
            new_virtual_lanes,
            segments_in_view,
            horizon,
            self.car,
            self._lazy_intersecting_cars.data,
            self._lazy_reserved_segments.data,
            self._lazy_claimed_segments.data
        )

    def _compute_intersecting_cars_in_view(self, old_cars: dict[str, dict[Segment, Interval]]):
        # only consider cars that intersect with the horizon
        new_intersecting_cars: dict[str, dict[Segment, Interval]] = dict()
        for intersecting_car, occupied_segment_interval in old_cars.items():
            # if there is any intersection with the horizon, we can put all the occupied segments of the car in the view
            # this won't break the logic and safes us computation time
            any_intersects = any(
                occupied_interval.intersects(self.horizon)
                for occupied_segment, occupied_interval in occupied_segment_interval.items()
            )
            if any_intersects:
                new_intersecting_cars[intersecting_car] = occupied_segment_interval

        return new_intersecting_cars

    def _compute_reserved_segments_in_view(self, old_reserved_segments: dict[str, dict[Segment, Interval]]):
        # only consider reserved segments that intersect with the horizon
        new_reserved_segments: dict[str, dict[Segment, Interval]] = dict()
        for car, reserved_segments in old_reserved_segments.items():
            new_reserved_car_segments: dict[Segment, Interval] = dict()
            for segment, interval in reserved_segments.items():
                # todo: potentially broken, check again
                if segment in self.segments_in_view and self.horizon.intersects(interval):
                    new_reserved_car_segments[segment] = interval

            new_reserved_segments[car] = new_reserved_car_segments

        return new_reserved_segments

    def _compute_claimed_segments_in_view(self, old_claimed_segments: dict[str, dict[Segment, Interval]]):
        # only consider claimed segments that intersect with the horizon
        new_claimed_segments: dict[str, dict[Segment, Interval]] = dict()
        for car, claimed_segments in old_claimed_segments.items():
            new_claimed_car_segments: dict[Segment, Interval] = dict()
            for segment, interval in claimed_segments.items():
                if segment in self.segments_in_view and self.horizon.intersects(interval):
                    new_claimed_car_segments[segment] = interval

            new_claimed_segments[car] = new_claimed_car_segments

        return new_claimed_segments

    def get_intersecting_cars(self):
        return self._lazy_intersecting_cars.acquire_data()

    def get_reserved_segments(self):
        return self._lazy_reserved_segments.acquire_data()

    def get_claimed_segments(self):
        return self._lazy_claimed_segments.acquire_data()
