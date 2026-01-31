from enum import Enum
from typing import Any, Optional

from sortedcontainers import SortedDict

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.helper.observables import ObservableDict, Observable, ReadOnlyDictView
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_validator import TrafficSnapshotValidator
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.view.view_constants import DIMENSION


class Direction(Enum):
    UP = "TOP"
    DOWN = "BOTTOM"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class TrafficSnapshotModel(Observable, TrafficSnapshotReader, TrafficSnapshotWriter):
    """
    Represents the complete state of a traffic simulation.

    Serves as the single source of truth for all roads and cars. Implements both
    TrafficSnapshotReader and TrafficSnapshotWriter interfaces for read/write access.

    Uses Observable pattern to notify observers of changes without PySide dependencies.

    Events:
        - TrafficSnapshotEventType.CAR_ADDED: Fired when a car is added (data: Car)
        - TrafficSnapshotEventType.CAR_REMOVED: Fired when a car is removed (data: Car)
        - TrafficSnapshotEventType.CAR_UPDATED: Fired when a car is updated (data: Car)
        - TrafficSnapshotEventType.ROAD_ADDED: Fired when a road is added (data: Road)
        - TrafficSnapshotEventType.ROAD_REMOVED: Fired when a road is removed (data: Road)
        - TrafficSnapshotEventType.ROAD_UPDATED: Fired when a road is updated (data: Road)
        # - TrafficSnapshotEventType.CROSSING_SEGMENT_ADDED: Fired when a crossing segment is added (data: CrossingSegment)
        # - TrafficSnapshotEventType.CROSSING_SEGMENT_REMOVED: Fired when a crossing segment is removed (data: CrossingSegment)
        # - TrafficSnapshotEventType.CROSSING_SEGMENT_UPDATED: Fired when a crossing segment is updated (data: CrossingSegment)
    """

    def get_next_road_in_front_of_car(self, car: Car) -> Road | None:
        pass

    def get_entity_by_uid(self, uid: str):
        pass

    def get_adjacent_segment(self, segment_uid: str, direction: Direction) -> Segment | None:
        if self._connections[segment_uid].get(direction) is not None:
            adjacent_uid = self._connections[segment_uid][direction]
            return self._segments.get(adjacent_uid)
        return None

    def get_lane_width(self):
        """Get the width of a single lane in the traffic snapshot.

        Returns:
            The width of a lane as a float.
        """
        return self.lane_width

    def get_road_by_uid(self, uid: str) -> Road | None:
        """Retrieve a road by its unique identifier (uid).

        Args:
            uid: The unique identifier of the road.

        Returns:
            The Road object if found, otherwise None.
        """
        if uid in self._horizontal_roads:
            return self._horizontal_roads[uid]
        elif uid in self._vertical_roads:
            return self._vertical_roads[uid]
        raise ValueError(f"Road with uid {uid} not found.")

    def __init__(
            self,
            roads: Optional[ObservableDict[str, Road]] = None,
            cars: Optional[ObservableDict[str, Car]] = None,
    ):

        super().__init__()
        self._cars = cars if cars is not None else ObservableDict[str, Car](
            on_add=lambda car: self.notify(TrafficSnapshotEventType.CAR_ADDED, car),
            on_remove=lambda car: self.notify(TrafficSnapshotEventType.CAR_REMOVED, car),
            on_update=lambda car: self.notify(TrafficSnapshotEventType.CAR_UPDATED, car)
        )

        self._horizontal_roads: ObservableDict[str, Road] = ObservableDict(
            on_add=self._on_road_added,
            on_remove=self._on_road_removed,
            on_update=self._on_road_updated
        )
        self._vertical_roads: ObservableDict[str, Road] = ObservableDict(
            on_add=self._on_road_added,
            on_remove=self._on_road_removed,
            on_update=self._on_road_updated
        )
        self._segments: dict[str, Segment] = {}
        """Dictionary of segments, keyed by their uid."""
        self._connections: dict[str, dict[Direction, str]] = {}
        """Dictionary of segment connections, keyed by segment uid. And in the direction dict all connected segments uids."""
        self._segments_by_lane: dict[int, list[str]] = {}
        """Dictionary mapping the hash(lane) to their corresponding segment uids."""

        self._read_only_roads = ReadOnlyDictView(self._horizontal_roads + self._vertical_roads)
        """Read-only view of the roads dictionary."""
        self._read_only_cars = ReadOnlyDictView(self._cars)
        """Read-only view of the cars dictionary."""

        self.lane_width = DIMENSION.LANE_WIDTH

        self.validator = TrafficSnapshotValidator(self)

    @property
    def cars(self):
        return self._read_only_cars

    @property
    def roads(self):
        return self._read_only_roads

    def _on_road_added(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_ADDED, road)

    def _on_road_removed(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_REMOVED, road)

    def _on_road_updated(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_UPDATED, road)
        self.validator.validate_road(road, False)

    def get_cars_on_road(self, road: Road) -> list[Car]:
        pass

    def get_cars(self) -> list[Car]:
        pass

    def get_roads(self) -> list[Road]:
        pass

    def get_cars_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Car]:
        pass

    def get_roads_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Road]:
        pass

    def get_max_velocity(self) -> float:
        pass

    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool:
        pass

    def add_road(self, road: Road) -> None:
        self.validator.validate_road(road, True)
        if road.orientation == RoadOrientation.HORIZONTAL:
            self._horizontal_roads[road.uid] = road
        else:
            self._vertical_roads[road.uid] = road
        self._recalculate_static_segments()

    def remove_road(self, road_uid: str) -> None:
        if road_uid in self._horizontal_roads:
            self._horizontal_roads.pop(road_uid)
        elif road_uid in self._vertical_roads:
            self._vertical_roads.pop(road_uid)
        self._recalculate_static_segments()

    def update_road(self, road_data: Road) -> None:
        self.validator.validate_road(road_data, False)
        pass

    def add_car(self, car: Car) -> None:
        self.validator.validate_car(car, True)
        self._cars[car.name] = car

    def remove_car(self, car_name: str) -> None:
        self._cars.pop(car_name)

    def update_car(self, car_data: Car) -> None:
        self.validator.validate_car(car_data, False)
        pass

    def _recalculate_car_claimed_and_reserved_segments(self, car: Car) -> None:
        # calculate claimed segments

        # calculate reserved segments

        pass

    def _get_car_tail_segment(self, car: Car) -> Segment:
        car_tail_position = car.get_tail_position(self)
        for segment_uid in self._segments_by_lane[hash(car.lane)]:
            segment = self._get_segment_by_uid(segment_uid)
            segment_position = segment.get_position(self)
            segment_size = segment.get_size(self)
            if segment_position[0] <= car_tail_position[0] <= segment_position[0] + segment_size[0] and \
               segment_position[1] <= car_tail_position[1] <= segment_position[1] + segment_size[1]:
                return segment
        raise ValueError(f"Car tail segment not found for car {car.name}.")

    def _get_segment_by_uid(self, segment_uid: str) -> Segment:
        segment = self._segments.get(segment_uid)
        if segment is None:
            raise ValueError(f"Segment with uid {segment_uid} not found.")
        return segment
    def _recalculate_static_segments(self) -> None:
        """
        Recalculates all static segments in the traffic snapshot.

        Builds a graph of segments representing the road network:
        - CrossingSegments: where a horizontal lane crosses a vertical lane
        - LaneSegments: parts of lanes between crossing "blocks" (or extending to infinity at bounds)

        Connections:
        - Each segment connects to adjacent segments in 4 directions (TOP, BOTTOM, LEFT, RIGHT)
        - Crossing segments connect to adjacent crossing segments within the same intersection
        - Lane segments connect to the boundary crossing segments of an intersection
        - Parallel lanes in the same direction are bidirectionally connected for lane switching

        _segments_by_lane maps each lane uid to ordered segment uids
        (left-to-right for horizontal, top-to-bottom for vertical).
        """
        # Clear existing data
        self._segments.clear()
        self._connections.clear()
        self._segments_by_lane.clear()

        # Get sorted lists of roads by position
        h_roads_sorted = sorted(self._horizontal_roads.values(), key=lambda r: r.position)
        v_roads_sorted = sorted(self._vertical_roads.values(), key=lambda r: r.position)

        # Collect all lanes per road, maintaining order
        # For each road: backward lanes (negative indices) then forward lanes (positive indices)
        # Lanes are ordered from "lower" to "higher" position perpendicular to road direction

        def get_ordered_lanes(road: Road) -> list[Lane]:
            """Get lanes ordered by their perpendicular position (backward first, then forward)."""
            # Backward lanes have negative indices, forward have non-negative
            # Order: most negative first, then ascending
            return sorted(road.backward_lanes + road.forward_lanes, key=lambda l: l.lane_index)

        # Create crossing segments for each intersection
        # crossing_grid[v_road_idx][h_road_idx] is a 2D grid of crossings for that intersection
        # Each grid cell is indexed by (h_lane_idx_in_road, v_lane_idx_in_road)
        crossing_grid: dict[int, dict[int, dict[tuple[int, int], CrossingSegment]]] = {}

        for v_road_idx, v_road in enumerate(v_roads_sorted):
            crossing_grid[v_road_idx] = {}
            v_lanes = get_ordered_lanes(v_road)

            for h_road_idx, h_road in enumerate(h_roads_sorted):
                crossing_grid[v_road_idx][h_road_idx] = {}
                h_lanes = get_ordered_lanes(h_road)

                for h_lane_local_idx, h_lane in enumerate(h_lanes):
                    for v_lane_local_idx, v_lane in enumerate(v_lanes):
                        crossing = CrossingSegment(
                            horizontal_lane=h_lane,
                            vertical_lane=v_lane
                        )
                        crossing_grid[v_road_idx][h_road_idx][(h_lane_local_idx, v_lane_local_idx)] = crossing
                        self._segments[crossing.uid] = crossing
                        self._connections[crossing.uid] = {}

        # Connect crossing segments within each intersection (to adjacent crossings)
        for v_road_idx, v_road in enumerate(v_roads_sorted):
            v_lanes = get_ordered_lanes(v_road)

            for h_road_idx, h_road in enumerate(h_roads_sorted):
                h_lanes = get_ordered_lanes(h_road)
                grid = crossing_grid[v_road_idx][h_road_idx]

                for h_lane_local_idx in range(len(h_lanes)):
                    for v_lane_local_idx in range(len(v_lanes)):
                        crossing = grid[(h_lane_local_idx, v_lane_local_idx)]

                        # Connect to RIGHT neighbor (next v_lane within same intersection)
                        if v_lane_local_idx + 1 < len(v_lanes):
                            right_crossing = grid[(h_lane_local_idx, v_lane_local_idx + 1)]
                            self._connections[crossing.uid][Direction.RIGHT] = right_crossing.uid
                            self._connections[right_crossing.uid][Direction.LEFT] = crossing.uid

                        # Connect to BOTTOM neighbor (next h_lane within same intersection)
                        if h_lane_local_idx + 1 < len(h_lanes):
                            bottom_crossing = grid[(h_lane_local_idx + 1, v_lane_local_idx)]
                            self._connections[crossing.uid][Direction.DOWN] = bottom_crossing.uid
                            self._connections[bottom_crossing.uid][Direction.UP] = crossing.uid

        # Create lane segments and connect them
        # For horizontal lanes: segments between vertical roads (and at boundaries)
        for h_road_idx, h_road in enumerate(h_roads_sorted):
            h_lanes = get_ordered_lanes(h_road)

            for h_lane_local_idx, h_lane in enumerate(h_lanes):
                lane_segment_uids: list[str] = []

                # Number of lane segments = number of vertical roads + 1
                num_v_roads = len(v_roads_sorted)

                for seg_idx in range(num_v_roads + 1):
                    lane_seg = LaneSegment(lane=h_lane)
                    self._segments[lane_seg.uid] = lane_seg
                    self._connections[lane_seg.uid] = {}
                    lane_segment_uids.append(lane_seg.uid)

                    # Connect to LEFT: either previous intersection's rightmost crossing, or nothing (infinity)
                    if seg_idx > 0:
                        prev_v_road_idx = seg_idx - 1
                        v_lanes_prev = get_ordered_lanes(v_roads_sorted[prev_v_road_idx])
                        # Rightmost crossing of previous intersection (highest v_lane_local_idx)
                        rightmost_crossing = crossing_grid[prev_v_road_idx][h_road_idx][(h_lane_local_idx, len(v_lanes_prev) - 1)]
                        self._connections[lane_seg.uid][Direction.LEFT] = rightmost_crossing.uid
                        self._connections[rightmost_crossing.uid][Direction.RIGHT] = lane_seg.uid

                    # Connect to RIGHT: next intersection's leftmost crossing, or nothing (infinity)
                    if seg_idx < num_v_roads:
                        next_v_road_idx = seg_idx
                        # Leftmost crossing of next intersection (v_lane_local_idx = 0)
                        leftmost_crossing = crossing_grid[next_v_road_idx][h_road_idx][(h_lane_local_idx, 0)]
                        self._connections[lane_seg.uid][Direction.RIGHT] = leftmost_crossing.uid
                        self._connections[leftmost_crossing.uid][Direction.LEFT] = lane_seg.uid

                    # Add crossings for this segment position to the lane's segment list
                    if seg_idx < num_v_roads:
                        v_lanes_at_idx = get_ordered_lanes(v_roads_sorted[seg_idx])
                        for v_lane_local_idx in range(len(v_lanes_at_idx)):
                            crossing = crossing_grid[seg_idx][h_road_idx][(h_lane_local_idx, v_lane_local_idx)]
                            lane_segment_uids.append(crossing.uid)

                self._segments_by_lane[hash(h_lane)] = lane_segment_uids

        # For vertical lanes: segments between horizontal roads (and at boundaries)
        for v_road_idx, v_road in enumerate(v_roads_sorted):
            v_lanes = get_ordered_lanes(v_road)

            for v_lane_local_idx, v_lane in enumerate(v_lanes):
                lane_segment_uids: list[str] = []

                num_h_roads = len(h_roads_sorted)

                for seg_idx in range(num_h_roads + 1):
                    lane_seg = LaneSegment(lane=v_lane)
                    self._segments[lane_seg.uid] = lane_seg
                    self._connections[lane_seg.uid] = {}
                    lane_segment_uids.append(lane_seg.uid)

                    # Connect to TOP: previous intersection's bottommost crossing, or nothing (infinity)
                    if seg_idx > 0:
                        prev_h_road_idx = seg_idx - 1
                        h_lanes_prev = get_ordered_lanes(h_roads_sorted[prev_h_road_idx])
                        # Bottommost crossing of previous intersection (highest h_lane_local_idx)
                        bottommost_crossing = crossing_grid[v_road_idx][prev_h_road_idx][(len(h_lanes_prev) - 1, v_lane_local_idx)]
                        self._connections[lane_seg.uid][Direction.UP] = bottommost_crossing.uid
                        self._connections[bottommost_crossing.uid][Direction.DOWN] = lane_seg.uid

                    # Connect to BOTTOM: next intersection's topmost crossing, or nothing (infinity)
                    if seg_idx < num_h_roads:
                        next_h_road_idx = seg_idx
                        # Topmost crossing of next intersection (h_lane_local_idx = 0)
                        topmost_crossing = crossing_grid[v_road_idx][next_h_road_idx][(0, v_lane_local_idx)]
                        self._connections[lane_seg.uid][Direction.DOWN] = topmost_crossing.uid
                        self._connections[topmost_crossing.uid][Direction.UP] = lane_seg.uid

                    # Add crossings for this segment position to the lane's segment list
                    if seg_idx < num_h_roads:
                        h_lanes_at_idx = get_ordered_lanes(h_roads_sorted[seg_idx])
                        for h_lane_local_idx in range(len(h_lanes_at_idx)):
                            crossing = crossing_grid[v_road_idx][seg_idx][(h_lane_local_idx, v_lane_local_idx)]
                            lane_segment_uids.append(crossing.uid)

                self._segments_by_lane[hash(v_lane)] = lane_segment_uids

        # Connect parallel lanes in the same direction (bidirectional for lane switching)
        self._connect_parallel_lanes(h_roads_sorted, v_roads_sorted, get_ordered_lanes)
        self.notify(TrafficSnapshotEventType.SEGMENTS_RECALCULATED, self._segments.values())

    def _connect_parallel_lanes(
        self,
        h_roads_sorted: list[Road],
        v_roads_sorted: list[Road],
        get_ordered_lanes
    ) -> None:
        """
        Connect parallel lanes in the same direction for lane switching.
        Connections are bidirectional - cars can switch from lane1 to lane2 and vice versa.

        For horizontal roads: adjacent lanes connect via TOP/BOTTOM
        For vertical roads: adjacent lanes connect via LEFT/RIGHT

        Only lanes going in the same direction on the same road are connected.
        """

        def same_direction(lane1: Lane, lane2: Lane) -> bool:
            """Check if two lanes are going in the same direction."""
            # Forward lanes have non-negative index, backward have negative
            return (lane1.lane_index >= 0) == (lane2.lane_index >= 0)

        # Connect horizontal lanes
        for h_road in h_roads_sorted:
            h_lanes = get_ordered_lanes(h_road)

            for i in range(len(h_lanes) - 1):
                lane1 = h_lanes[i]
                lane2 = h_lanes[i + 1]

                if not same_direction(lane1, lane2):
                    continue

                segments1 = self._segments_by_lane.get(lane1.uid, [])
                segments2 = self._segments_by_lane.get(lane2.uid, [])

                if len(segments1) != len(segments2):
                    continue

                # lane1 has lower index, so it's "above" lane2 (TOP/BOTTOM connection)
                for seg1_uid, seg2_uid in zip(segments1, segments2):
                    seg1 = self._segments.get(seg1_uid)
                    seg2 = self._segments.get(seg2_uid)

                    if seg1 is None or seg2 is None:
                        continue

                    # Only connect same types (lane to lane, crossing to crossing)
                    if seg1.is_lane_segment != seg2.is_lane_segment:
                        continue

                    # Bidirectional connection
                    self._connections[seg1_uid][Direction.DOWN] = seg2_uid
                    self._connections[seg2_uid][Direction.UP] = seg1_uid

        # Connect vertical lanes
        for v_road in v_roads_sorted:
            v_lanes = get_ordered_lanes(v_road)

            for i in range(len(v_lanes) - 1):
                lane1 = v_lanes[i]
                lane2 = v_lanes[i + 1]

                if not same_direction(lane1, lane2):
                    continue

                segments1 = self._segments_by_lane.get(lane1.uid, [])
                segments2 = self._segments_by_lane.get(lane2.uid, [])

                if len(segments1) != len(segments2):
                    continue

                # lane1 has lower index, so it's "left" of lane2 (LEFT/RIGHT connection)
                for seg1_uid, seg2_uid in zip(segments1, segments2):
                    seg1 = self._segments.get(seg1_uid)
                    seg2 = self._segments.get(seg2_uid)

                    if seg1 is None or seg2 is None:
                        continue

                    if seg1.is_lane_segment != seg2.is_lane_segment:
                        continue

                    # Bidirectional connection
                    self._connections[seg1_uid][Direction.RIGHT] = seg2_uid
                    self._connections[seg2_uid][Direction.LEFT] = seg1_uid

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the TrafficSnapshot instance to a dictionary suitable for JSON encoding.
        """
        raise NotImplementedError

    def to_json(self) -> str:
        """
        Serializes the TrafficSnapshot instance to a JSON string.
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrafficSnapshotModel":
        """
        Creates a TrafficSnapshot instance from a dictionary.

        Args:
            data: A dictionary containing 'roads' and 'cars' keys.
        """
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_string: str) -> "TrafficSnapshotModel":
        """
        Creates a TrafficSnapshot instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing traffic snapshot data.

        """
        raise NotImplementedError
