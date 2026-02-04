from typing import Any

import networkx as nx

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_validator import TrafficSnapshotValidator
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType
from pse.umlsl_editor.src.model.helper.observables import ObservableDict, Observable, ReadOnlyDictView
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import CrossingSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import LaneSegment
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.view.view_constants import DIMENSION


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

    def get_scene_size(self) -> float:
        pass

    def is_road_existing(self, uid: str) -> bool:
        if uid in self._horizontal_roads or uid in self._vertical_roads:
            return True
        return False

    def is_car_existing(self, uid: str) -> bool:
        return uid in self._cars

    def validate_road_params(self, road_params: RoadParams, new_instantiation: bool) -> None:
        self.validator.validate_road_params(road_params, new_instantiation)

    def validate_car_params(self, car_params: CarParams, new_instantiation: bool) -> None:
        self.validator.validate_car_params(car_params, new_instantiation)

    def get_next_road_in_front_of_car(self, car: Car) -> Road | None:
        pass

    def get_entity_by_uid(self, uid: str):
        pass

    def get_adjacent_segment(self, segment_uid: str, direction: Direction) -> Segment | None:
        adjacent_uid = self._get_neighbor_in_direction(segment_uid, direction)
        if adjacent_uid is not None:
            return self._segments[adjacent_uid]
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
            roads: ObservableDict[str, Road] | None = None,
            cars: ObservableDict[str, Car] | None = None,
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
        # self._connections: dict[str, dict[Direction, str]] = {}
        # """Dictionary of segment connections, keyed by segment uid. And in the direction dict all connected segments uids."""
        self._segments_by_lane: dict[int, list[str]] = {}
        """Dictionary mapping the hash(lane) to their corresponding segment uids."""
        self._graph = nx.DiGraph()
        """Graph representing the connectivity of segments."""

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
        self._recalculate_static_segments()

    def _on_road_removed(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_REMOVED, road)
        self._recalculate_static_segments()

    def _on_road_updated(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_UPDATED, road)
        self._recalculate_static_segments()

    def get_cars_on_road(self, road: Road) -> list[Car]:
        return [car for car in self._cars.values() if car.lane.road_uid == road.uid]

    def get_cars(self) -> dict[str, Car]:
        return dict(self._read_only_cars)

    def get_roads(self) -> dict[str, Road]:
        return {**self._horizontal_roads, **self._vertical_roads}

    def get_cars_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Car]:
        pass

    def get_roads_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Road]:
        pass

    def get_max_velocity(self) -> float:
        pass

    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool:
        pass

    def add_road(self, road: Road) -> None:
        if road.orientation == RoadOrientation.HORIZONTAL:
            self._horizontal_roads[road.uid] = road
        else:
            self._vertical_roads[road.uid] = road
        # self._recalculate_static_segments()

    def remove_road(self, road_uid: str) -> None:
        if road_uid in self._horizontal_roads:
            self._horizontal_roads.pop(road_uid)
        elif road_uid in self._vertical_roads:
            self._vertical_roads.pop(road_uid)
        # self._recalculate_static_segments()

    def update_road(self, road_uid: str, road_params: RoadParams) -> None:
        road = self.get_road_by_uid(road_uid)
        original_orientation = road.orientation

        road.update_from_params(road_params)

        if original_orientation != road.orientation:
            if original_orientation == RoadOrientation.HORIZONTAL:
                del self._horizontal_roads[road_uid]
                self._vertical_roads[road_uid] = road
            else:
                del self._vertical_roads[road_uid]
                self._horizontal_roads[road_uid] = road
        else:
            if road.orientation == RoadOrientation.HORIZONTAL:
                self._horizontal_roads[road_uid] = road
            else:
                self._vertical_roads[road_uid] = road

        # self._recalculate_static_segments()

    def add_car(self, car: Car) -> None:
        self._cars[car.uid] = car

    def remove_car(self, car_uid: str) -> None:
        self._cars.pop(car_uid)

    def update_car_with_params(self, car_uid: str, car_params: CarParams) -> None:
        car = self._cars.get(car_uid)
        car.update_from_params(car_params)
        self._cars[car_uid] = car

    def _recalculate_car_claimed_and_reserved_segments(self, car: Car) -> None:
        # calculate claimed segments

        # calculate reserved segments

        pass

    def _get_car_tail_segment(self, car: Car) -> Segment:
        """
        Get the segment where the tail of the car is positioned.

        Args:
            car: The car to find the tail segment for.

        Returns:
            The Segment containing the car's tail position.

        Raises:
            ValueError: If the car's lane has no segments or segment not found.
        """
        tail_x, tail_y = car.get_tail_position(self)

        lane_hash = hash(car.lane)
        if lane_hash not in self._segments_by_lane:
            raise ValueError(f"Lane {car.lane} not found in segment map.")

        segment_uids = self._segments_by_lane[lane_hash]

        # Determine orientation
        road = self.get_road_by_uid(car.lane.road_uid)
        orientation = road.orientation

        target_pos = tail_x if orientation == RoadOrientation.HORIZONTAL else tail_y

        for uid in segment_uids:
            segment = self._segments[uid]
            start, end = self._get_segment_position_bounds(segment, orientation)

            if start <= target_pos <= end:
                return segment

        raise ValueError(f"Could not find segment for car tail at {target_pos} on lane {car.lane}")

    def _get_lane_segment_bounds(self, segment: LaneSegment, orientation: RoadOrientation) -> tuple[float, float]:
        """
        Get the start and end position of a lane segment along the lane axis.

        Returns:
            Tuple of (start_position, end_position) along the lane axis.
        """
        lane = segment.lane

        # Find the adjacent crossing segments or boundaries
        if orientation == RoadOrientation.HORIZONTAL:
            left_neighbor_uid = self._get_neighbor_in_direction(segment.uid, Direction.LEFT)
            right_neighbor_uid = self._get_neighbor_in_direction(segment.uid, Direction.RIGHT)

            if left_neighbor_uid is None:
                start = float('-inf')
            else:
                left_segment = self._segments[left_neighbor_uid]
                if isinstance(left_segment, CrossingSegment):
                    v_road = self.get_road_by_uid(left_segment.vertical_lane.road_uid)
                    start = v_road.position + self.lane_width
                else:
                    start = float('-inf')

            if right_neighbor_uid is None:
                end = float('inf')
            else:
                right_segment = self._segments[right_neighbor_uid]
                if isinstance(right_segment, CrossingSegment):
                    v_road = self.get_road_by_uid(right_segment.vertical_lane.road_uid)
                    end = v_road.position
                else:
                    end = float('inf')
        else:
            # Vertical orientation
            up_neighbor_uid = self._get_neighbor_in_direction(segment.uid, Direction.UP)
            down_neighbor_uid = self._get_neighbor_in_direction(segment.uid, Direction.DOWN)

            if up_neighbor_uid is None:
                start = float('-inf')
            else:
                up_segment = self._segments[up_neighbor_uid]
                if isinstance(up_segment, CrossingSegment):
                    h_road = self.get_road_by_uid(up_segment.horizontal_lane.road_uid)
                    start = h_road.position + self.lane_width
                else:
                    start = float('-inf')

            if down_neighbor_uid is None:
                end = float('inf')
            else:
                down_segment = self._segments[down_neighbor_uid]
                if isinstance(down_segment, CrossingSegment):
                    h_road = self.get_road_by_uid(down_segment.horizontal_lane.road_uid)
                    end = h_road.position
                else:
                    end = float('inf')

        return start, end

    def _get_segment_position_bounds(self, segment: Segment, orientation: RoadOrientation) -> tuple[float, float]:
        """Get position bounds for any segment type."""
        if isinstance(segment, LaneSegment):
            return self._get_lane_segment_bounds(segment, orientation)
        elif isinstance(segment, CrossingSegment):
            if orientation == RoadOrientation.HORIZONTAL:
                v_road = self.get_road_by_uid(segment.vertical_lane.road_uid)
                return v_road.position, v_road.position + self.lane_width
            else:
                h_road = self.get_road_by_uid(segment.horizontal_lane.road_uid)
                return h_road.position, h_road.position + self.lane_width
        return float('-inf'), float('inf')

    def _get_neighbor_in_direction(self, segment_uid: str, direction: Direction) -> str | None:
        """Get the neighboring segment UID in a given direction from the graph."""
        for _, neighbor, data in self._graph.out_edges(segment_uid, data=True):
            if data.get('direction') == direction:
                return neighbor
        for neighbor, _, data in self._graph.in_edges(segment_uid, data=True):
            if data.get('direction') == direction.opposite:
                return neighbor
        return None

    def _get_segment_by_uid(self, segment_uid: str) -> Segment:
        segment = self._segments.get(segment_uid)
        if segment is None:
            raise ValueError(f"Segment with uid {segment_uid} not found.")
        return segment

    def _recalculate_static_segments(self) -> None:
        """
        Recalculate all static segments and their connections based on current roads.

        This builds:
        - CrossingSegments where horizontal and vertical lanes intersect
        - LaneSegments between crossings and at the boundaries (connecting to infinity)
        - Graph connections between all segments
        - _segments_by_lane mapping for quick car position lookup
        """
        self._segments.clear()
        self._segments_by_lane.clear()
        self._graph.clear()

        horizontal_roads = sorted(self._horizontal_roads.values(), key=lambda r: r.position)
        vertical_roads = sorted(self._vertical_roads.values(), key=lambda r: r.position)

        # 1. Create all CrossingSegments
        # Key: (horizontal_lane, vertical_lane) -> CrossingSegment
        crossing_map: dict[tuple[Lane, Lane], CrossingSegment] = {}

        for h_road in horizontal_roads:
            for v_road in vertical_roads:
                h_lanes = h_road.forward_lanes + h_road.backward_lanes
                v_lanes = v_road.forward_lanes + v_road.backward_lanes
                for h_lane in h_lanes:
                    for v_lane in v_lanes:
                        cs = CrossingSegment(horizontal_lane=h_lane, vertical_lane=v_lane)
                        self._segments[cs.uid] = cs
                        crossing_map[(h_lane, v_lane)] = cs

        # 2. Process Horizontal Roads
        for h_road in horizontal_roads:
            h_lanes = h_road.forward_lanes + h_road.backward_lanes
            # Sort Top to Bottom for Lateral connections
            h_lanes.sort(key=lambda l: l.lane_index)

            lane_physical_segments: dict[Lane, list[Segment]] = {}

            for lane in h_lanes:
                segments = []
                # Left Inf
                left_inf = LaneSegment(lane=lane)
                self._segments[left_inf.uid] = left_inf
                segments.append(left_inf)

                for v_road in vertical_roads:
                    v_lanes = sorted(v_road.forward_lanes + v_road.backward_lanes, key=lambda l: l.lane_index)
                    for v_lane in v_lanes:
                        segments.append(crossing_map[(lane, v_lane)])

                    mid_seg = LaneSegment(lane=lane)
                    self._segments[mid_seg.uid] = mid_seg
                    segments.append(mid_seg)

                lane_physical_segments[lane] = segments

                # Flow Direction Setup
                if lane.lane_index >= 0:
                    flow_uids = [s.uid for s in reversed(segments)]
                    flow_dir = Direction.LEFT
                else:
                    flow_uids = [s.uid for s in segments]
                    flow_dir = Direction.RIGHT

                self._segments_by_lane[hash(lane)] = flow_uids

                # Connect Flow
                for i in range(len(flow_uids) - 1):
                    self._graph.add_edge(flow_uids[i], flow_uids[i + 1], direction=flow_dir)

            # Connect Lateral
            for i in range(len(h_lanes) - 1):
                top_lane = h_lanes[i]
                bottom_lane = h_lanes[i + 1]

                segs_top = lane_physical_segments[top_lane]
                segs_bottom = lane_physical_segments[bottom_lane]

                for s_t, s_b in zip(segs_top, segs_bottom):
                    # Only connect LaneSegments laterally, not CrossingSegments
                    if isinstance(s_t, LaneSegment) and isinstance(s_b, LaneSegment):
                        self._graph.add_edge(s_t.uid, s_b.uid, direction=Direction.DOWN)
                        self._graph.add_edge(s_b.uid, s_t.uid, direction=Direction.UP)

        # 3. Process Vertical Roads
        for v_road in vertical_roads:
            v_lanes = v_road.forward_lanes + v_road.backward_lanes
            # Sort Left to Right
            v_lanes.sort(key=lambda l: l.lane_index)

            lane_physical_segments: dict[Lane, list[Segment]] = {}

            for lane in v_lanes:
                segments = []
                # Top Inf
                top_inf = LaneSegment(lane=lane)
                self._segments[top_inf.uid] = top_inf
                segments.append(top_inf)

                for h_road in horizontal_roads:
                    h_lanes = sorted(h_road.forward_lanes + h_road.backward_lanes, key=lambda l: l.lane_index)
                    for h_lane in h_lanes:
                        segments.append(crossing_map[(h_lane, lane)])

                    mid_seg = LaneSegment(lane=lane)
                    self._segments[mid_seg.uid] = mid_seg
                    segments.append(mid_seg)

                lane_physical_segments[lane] = segments

                # Flow Direction Setup
                if lane.lane_index >= 0:
                    flow_uids = [s.uid for s in segments]
                    flow_dir = Direction.DOWN
                else:
                    flow_uids = [s.uid for s in reversed(segments)]
                    flow_dir = Direction.UP

                self._segments_by_lane[hash(lane)] = flow_uids

                # Connect Flow
                for i in range(len(flow_uids) - 1):
                    self._graph.add_edge(flow_uids[i], flow_uids[i + 1], direction=flow_dir)

            # Connect Lateral
            for i in range(len(v_lanes) - 1):
                left_lane = v_lanes[i]
                right_lane = v_lanes[i + 1]

                segs_left = lane_physical_segments[left_lane]
                segs_right = lane_physical_segments[right_lane]

                for s_l, s_r in zip(segs_left, segs_right):
                    # Only connect LaneSegments laterally, not CrossingSegments
                    if isinstance(s_l, LaneSegment) and isinstance(s_r, LaneSegment):
                        self._graph.add_edge(s_l.uid, s_r.uid, direction=Direction.RIGHT)
                        self._graph.add_edge(s_r.uid, s_l.uid, direction=Direction.LEFT)

        self.print_graph()

    def print_graph(self) -> None:
        """
        Prints the graph structure to stdout for debugging purposes.
        Shows segments and their outgoing connections with directions.
        """
        print("=== Traffic Graph Structure ===")
        for segment_uid in self._graph.nodes:
            segment_info = self._get_segment_info_string(segment_uid)
            print(f"\n[Segment] {segment_info}")

            # Print outgoing connections
            out_edges = self._graph.out_edges(segment_uid, data=True)
            if not out_edges:
                print("  -> (no outgoing connections)")
            else:
                for _, target_uid, data in out_edges:
                    direction = data.get('direction')
                    direction_name = direction.name if direction else "UNKNOWN"
                    target_info = self._get_segment_info_string(target_uid)
                    print(f"  -> [{direction_name}] to {target_info}")
        print("===============================")

    def _get_segment_info_string(self, segment_uid: str) -> str:
        segment = self._segments.get(segment_uid)
        if segment is None:
            return f"UNKNOWN_SEGMENT({segment_uid})"

        if isinstance(segment, CrossingSegment):
            h_road = self.get_road_by_uid(segment.horizontal_lane.road_uid)
            v_road = self.get_road_by_uid(segment.vertical_lane.road_uid)
            return (f"CrossingSegment({segment_uid[:6]}...) "
                    f"at {h_road.name}(L{segment.horizontal_lane.lane_index}) x "
                    f"{v_road.name}(L{segment.vertical_lane.lane_index})")

        elif isinstance(segment, LaneSegment):
            road = self.get_road_by_uid(segment.lane.road_uid)
            return (f"LaneSegment({segment_uid[:6]}...) "
                    f"on road: {road.name}(L{segment.lane.lane_index})")

        return f"Segment({segment_uid[:6]}...)"

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

    def debug_get_segments(self) -> dict[str, Segment]:
        return self._segments

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
