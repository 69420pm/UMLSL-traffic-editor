from typing import Any

import networkx as nx

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_validator import TrafficSnapshotValidator
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.model.helper.directional_graph import Direction, DirectionalGraph
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType, SelectionEventType
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
        self._graph = DirectionalGraph()
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

    def _on_road_removed(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_REMOVED, road)

    def _on_road_updated(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_UPDATED, road)

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
        lane = car.lane
        lane_hash = hash(lane)

        if lane_hash not in self._segments_by_lane:
            raise ValueError(f"No segments found for lane {lane}")

        segment_uids = self._segments_by_lane[lane_hash]
        if not segment_uids:
            raise ValueError(f"Empty segment list for lane {lane}")

        # Get tail position
        tail_x, tail_y = car.get_tail_position(self)

        # Determine which coordinate to use based on road orientation
        road = self.get_road_by_uid(lane.road_uid)

        # The position along the lane axis
        if road.orientation == RoadOrientation.HORIZONTAL:
            tail_position = tail_x
        else:
            tail_position = tail_y

        # Iterate through segments to find which one contains the tail
        for segment_uid in segment_uids:
            segment = self._segments[segment_uid]

            if isinstance(segment, CrossingSegment):
                # For crossing segments, get the perpendicular road position
                if road.orientation == RoadOrientation.HORIZONTAL:
                    # Horizontal lane crosses vertical road
                    v_road = self.get_road_by_uid(segment.vertical_lane.road_uid)
                    seg_start = v_road.position
                    seg_end = seg_start + self.lane_width
                else:
                    # Vertical lane crosses horizontal road
                    h_road = self.get_road_by_uid(segment.horizontal_lane.road_uid)
                    seg_start = h_road.position
                    seg_end = seg_start + self.lane_width

                if seg_start <= tail_position < seg_end:
                    return segment

            elif isinstance(segment, LaneSegment):
                # For lane segments, calculate the start and end positions
                seg_start, seg_end = self._get_lane_segment_bounds(segment, road.orientation)

                if seg_start <= tail_position < seg_end:
                    return segment

        # If we didn't find an exact match, the car might be at the boundary
        # Return the first or last segment based on position
        first_segment = self._segments[segment_uids[0]]
        last_segment = self._segments[segment_uids[-1]]

        first_start, _ = self._get_segment_position_bounds(first_segment, road.orientation)
        _, last_end = self._get_segment_position_bounds(last_segment, road.orientation)

        if tail_position < first_start:
            return first_segment
        else:
            return last_segment

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
        # Clear existing data
        self._segments.clear()
        self._segments_by_lane.clear()
        self._graph.clear()

        # Get all lanes from roads
        horizontal_lanes: list[Lane] = []
        vertical_lanes: list[Lane] = []

        for road in self._horizontal_roads.values():
            horizontal_lanes.extend(road.forward_lanes)
            horizontal_lanes.extend(road.backward_lanes)

        for road in self._vertical_roads.values():
            vertical_lanes.extend(road.forward_lanes)
            vertical_lanes.extend(road.backward_lanes)

        # Sort vertical roads by X position (for horizontal lane traversal)
        sorted_vertical_roads = sorted(
            self._vertical_roads.values(),
            key=lambda r: r.position
        )

        # Sort horizontal roads by Y position (for vertical lane traversal)
        sorted_horizontal_roads = sorted(
            self._horizontal_roads.values(),
            key=lambda r: r.position
        )

        # Create crossing segments lookup: (h_lane_key, v_lane_key) -> CrossingSegment
        crossing_lookup: dict[tuple[int, int], CrossingSegment] = {}

        # Phase 1: Create all CrossingSegments
        for h_lane in horizontal_lanes:
            for v_lane in vertical_lanes:
                crossing = CrossingSegment(
                    horizontal_lane=h_lane,
                    vertical_lane=v_lane
                )
                self._segments[crossing.uid] = crossing
                self._graph.add_node(crossing.uid)
                crossing_lookup[(hash(h_lane), hash(v_lane))] = crossing

        # Phase 2: Create LaneSegments and build _segments_by_lane for horizontal lanes
        # Also connect segments along each horizontal lane
        for h_lane in horizontal_lanes:
            h_road = self.get_road_by_uid(h_lane.road_uid)
            lane_key = hash(h_lane)
            segments_for_lane: list[str] = []

            # Determine traffic direction for this lane
            # Forward lanes (index >= 0) go LEFT -> RIGHT
            # Backward lanes (index < 0) go RIGHT -> LEFT
            is_forward = h_lane.lane_index >= 0

            # Create lane segments between crossings (and at boundaries)
            # We need segments: before first crossing, between crossings, after last crossing
            prev_crossing: CrossingSegment | None = None

            for i, v_road in enumerate(sorted_vertical_roads):
                # Get the crossing for this horizontal lane at this vertical road
                v_lanes = v_road.forward_lanes + v_road.backward_lanes

                # For each vertical road, find the crossing with any of its lanes
                # Actually, we need the crossing with a specific vertical lane
                # But for lane segment purposes, we need the crossing that this h_lane has
                # with the innermost vertical lane (to define boundaries)

                # Get all crossings at this vertical road position for this horizontal lane
                crossings_at_v_road = [
                    crossing_lookup[(hash(h_lane), hash(v_lane))]
                    for v_lane in v_lanes
                    if (hash(h_lane), hash(v_lane)) in crossing_lookup
                ]

                if not crossings_at_v_road:
                    continue

                # Use the first crossing (they all have the same X position boundary)
                current_crossing = crossings_at_v_road[0]

                # Create lane segment before this crossing (or between prev and current)
                lane_seg = LaneSegment(lane=h_lane)
                self._segments[lane_seg.uid] = lane_seg
                self._graph.add_node(lane_seg.uid)

                # Add to lane's segment list
                segments_for_lane.append(lane_seg.uid)

                # Connect lane segment to crossings
                if prev_crossing is not None:
                    # Connect prev_crossing -> lane_seg -> current_crossing
                    if is_forward:
                        # Traffic flows LEFT -> RIGHT
                        self._graph.add_edge(prev_crossing.uid, lane_seg.uid, direction=Direction.RIGHT)
                        self._graph.add_edge(lane_seg.uid, prev_crossing.uid, direction=Direction.LEFT)
                    else:
                        # Traffic flows RIGHT -> LEFT
                        self._graph.add_edge(prev_crossing.uid, lane_seg.uid, direction=Direction.LEFT)
                        self._graph.add_edge(lane_seg.uid, prev_crossing.uid, direction=Direction.RIGHT)

                # Add all crossings at this vertical road to segments_for_lane
                for crossing in crossings_at_v_road:
                    segments_for_lane.append(crossing.uid)

                # Connect lane segment to current crossing
                if is_forward:
                    self._graph.add_edge(lane_seg.uid, current_crossing.uid, direction=Direction.RIGHT)
                    self._graph.add_edge(current_crossing.uid, lane_seg.uid, direction=Direction.LEFT)
                else:
                    self._graph.add_edge(lane_seg.uid, current_crossing.uid, direction=Direction.LEFT)
                    self._graph.add_edge(current_crossing.uid, lane_seg.uid, direction=Direction.RIGHT)

                prev_crossing = current_crossing

            # Create final lane segment after last crossing
            if sorted_vertical_roads:
                final_lane_seg = LaneSegment(lane=h_lane)
                self._segments[final_lane_seg.uid] = final_lane_seg
                self._graph.add_node(final_lane_seg.uid)
                segments_for_lane.append(final_lane_seg.uid)

                if prev_crossing is not None:
                    if is_forward:
                        self._graph.add_edge(prev_crossing.uid, final_lane_seg.uid, direction=Direction.RIGHT)
                        self._graph.add_edge(final_lane_seg.uid, prev_crossing.uid, direction=Direction.LEFT)
                    else:
                        self._graph.add_edge(prev_crossing.uid, final_lane_seg.uid, direction=Direction.LEFT)
                        self._graph.add_edge(final_lane_seg.uid, prev_crossing.uid, direction=Direction.RIGHT)
            elif not sorted_vertical_roads:
                # No vertical roads, create single lane segment spanning the whole lane
                single_lane_seg = LaneSegment(lane=h_lane)
                self._segments[single_lane_seg.uid] = single_lane_seg
                self._graph.add_node(single_lane_seg.uid)
                segments_for_lane.append(single_lane_seg.uid)

            self._segments_by_lane[lane_key] = segments_for_lane

        # Phase 3: Create LaneSegments for vertical lanes
        for v_lane in vertical_lanes:
            v_road = self.get_road_by_uid(v_lane.road_uid)
            lane_key = hash(v_lane)
            segments_for_lane: list[str] = []

            # Forward lanes (index >= 0) go TOP -> BOTTOM (UP -> DOWN in coordinates)
            # Backward lanes (index < 0) go BOTTOM -> TOP
            is_forward = v_lane.lane_index >= 0

            prev_crossing: CrossingSegment | None = None

            for i, h_road in enumerate(sorted_horizontal_roads):
                h_lanes = h_road.forward_lanes + h_road.backward_lanes

                crossings_at_h_road = [
                    crossing_lookup[(hash(h_lane), hash(v_lane))]
                    for h_lane in h_lanes
                    if (hash(h_lane), hash(v_lane)) in crossing_lookup
                ]

                if not crossings_at_h_road:
                    continue

                current_crossing = crossings_at_h_road[0]

                # Create lane segment before this crossing
                lane_seg = LaneSegment(lane=v_lane)
                self._segments[lane_seg.uid] = lane_seg
                self._graph.add_node(lane_seg.uid)
                segments_for_lane.append(lane_seg.uid)

                if prev_crossing is not None:
                    if is_forward:
                        # Traffic flows TOP -> BOTTOM (Direction.DOWN)
                        self._graph.add_edge(prev_crossing.uid, lane_seg.uid, direction=Direction.DOWN)
                        self._graph.add_edge(lane_seg.uid, prev_crossing.uid, direction=Direction.UP)
                    else:
                        self._graph.add_edge(prev_crossing.uid, lane_seg.uid, direction=Direction.UP)
                        self._graph.add_edge(lane_seg.uid, prev_crossing.uid, direction=Direction.DOWN)

                for crossing in crossings_at_h_road:
                    segments_for_lane.append(crossing.uid)

                if is_forward:
                    self._graph.add_edge(lane_seg.uid, current_crossing.uid, direction=Direction.DOWN)
                    self._graph.add_edge(current_crossing.uid, lane_seg.uid, direction=Direction.UP)
                else:
                    self._graph.add_edge(lane_seg.uid, current_crossing.uid, direction=Direction.UP)
                    self._graph.add_edge(current_crossing.uid, lane_seg.uid, direction=Direction.DOWN)

                prev_crossing = current_crossing

            # Final lane segment
            if sorted_horizontal_roads:
                final_lane_seg = LaneSegment(lane=v_lane)
                self._segments[final_lane_seg.uid] = final_lane_seg
                self._graph.add_node(final_lane_seg.uid)
                segments_for_lane.append(final_lane_seg.uid)

                if prev_crossing is not None:
                    if is_forward:
                        self._graph.add_edge(prev_crossing.uid, final_lane_seg.uid, direction=Direction.DOWN)
                        self._graph.add_edge(final_lane_seg.uid, prev_crossing.uid, direction=Direction.UP)
                    else:
                        self._graph.add_edge(prev_crossing.uid, final_lane_seg.uid, direction=Direction.UP)
                        self._graph.add_edge(final_lane_seg.uid, prev_crossing.uid, direction=Direction.DOWN)
            elif not sorted_horizontal_roads:
                single_lane_seg = LaneSegment(lane=v_lane)
                self._segments[single_lane_seg.uid] = single_lane_seg
                self._graph.add_node(single_lane_seg.uid)
                segments_for_lane.append(single_lane_seg.uid)

            self._segments_by_lane[lane_key] = segments_for_lane

        # Phase 4: Connect crossing segments along horizontal lanes (LEFT/RIGHT)
        for h_lane in horizontal_lanes:
            is_forward = h_lane.lane_index >= 0
            prev_crossing: CrossingSegment | None = None

            for v_road in sorted_vertical_roads:
                for v_lane in v_road.forward_lanes + v_road.backward_lanes:
                    key = (hash(h_lane), hash(v_lane))
                    if key in crossing_lookup:
                        current_crossing = crossing_lookup[key]

                        if prev_crossing is not None:
                            # Connect horizontally adjacent crossing segments
                            if is_forward:
                                self._graph.add_edge(prev_crossing.uid, current_crossing.uid, direction=Direction.RIGHT)
                                self._graph.add_edge(current_crossing.uid, prev_crossing.uid, direction=Direction.LEFT)
                            else:
                                self._graph.add_edge(current_crossing.uid, prev_crossing.uid, direction=Direction.RIGHT)
                                self._graph.add_edge(prev_crossing.uid, current_crossing.uid, direction=Direction.LEFT)

                        prev_crossing = current_crossing

        # Phase 5: Connect crossing segments along vertical lanes (UP/DOWN)
        for v_lane in vertical_lanes:
            is_forward = v_lane.lane_index >= 0
            prev_crossing: CrossingSegment | None = None

            for h_road in sorted_horizontal_roads:
                for h_lane in h_road.forward_lanes + h_road.backward_lanes:
                    key = (hash(h_lane), hash(v_lane))
                    if key in crossing_lookup:
                        current_crossing = crossing_lookup[key]

                        if prev_crossing is not None:
                            if is_forward:
                                self._graph.add_edge(prev_crossing.uid, current_crossing.uid, direction=Direction.DOWN)
                                self._graph.add_edge(current_crossing.uid, prev_crossing.uid, direction=Direction.UP)
                            else:
                                self._graph.add_edge(current_crossing.uid, prev_crossing.uid, direction=Direction.DOWN)
                                self._graph.add_edge(prev_crossing.uid, current_crossing.uid, direction=Direction.UP)

                        prev_crossing = current_crossing

        # Phase 6: Connect parallel lanes on the same road (undirected/bidirectional)
        self._connect_parallel_lanes_on_road(horizontal_lanes, sorted_vertical_roads, crossing_lookup, is_horizontal=True)
        self._connect_parallel_lanes_on_road(vertical_lanes, sorted_horizontal_roads, crossing_lookup, is_horizontal=False)

    def _connect_parallel_lanes_on_road(
        self,
        lanes: list[Lane],
        sorted_perpendicular_roads: list[Road],
        crossing_lookup: dict[tuple[int, int], CrossingSegment],
        is_horizontal: bool
    ) -> None:
        """
        Connect parallel lane segments and crossing segments on the same road.
        All parallel lanes (same or different direction) are connected undirectionally.
        """
        # Group lanes by road
        lanes_by_road: dict[str, list[Lane]] = {}
        for lane in lanes:
            road_uid = lane.road_uid
            if road_uid not in lanes_by_road:
                lanes_by_road[road_uid] = []
            lanes_by_road[road_uid].append(lane)

        for road_uid, road_lanes in lanes_by_road.items():
            # Sort lanes by index to find adjacent ones
            sorted_lanes = sorted(road_lanes, key=lambda l: l.lane_index)

            # Connect adjacent lanes
            for i in range(len(sorted_lanes) - 1):
                lane_a = sorted_lanes[i]
                lane_b = sorted_lanes[i + 1]

                # Get segments for both lanes
                lane_a_segments = self._segments_by_lane.get(hash(lane_a), [])
                lane_b_segments = self._segments_by_lane.get(hash(lane_b), [])

                # Connect corresponding lane segments (same region)
                # Lane segments are at the same indices in their respective lists
                # (before crossing 0, after crossing 0/before crossing 1, etc.)

                # Extract only lane segments (not crossings) for parallel connection
                lane_a_lane_segs = [uid for uid in lane_a_segments if isinstance(self._segments.get(uid), LaneSegment)]
                lane_b_lane_segs = [uid for uid in lane_b_segments if isinstance(self._segments.get(uid), LaneSegment)]

                # Connect lane segments in the same region
                for seg_a_uid, seg_b_uid in zip(lane_a_lane_segs, lane_b_lane_segs):
                    # Undirected connection - add edges in both directions
                    # Use UP/DOWN for horizontal lanes (adjacent lanes are vertically arranged)
                    # Use LEFT/RIGHT for vertical lanes (adjacent lanes are horizontally arranged)
                    if is_horizontal:
                        # Lane with higher index is below (higher Y)
                        self._graph.add_edge(seg_a_uid, seg_b_uid, direction=Direction.DOWN)
                        self._graph.add_edge(seg_b_uid, seg_a_uid, direction=Direction.UP)
                    else:
                        # Lane with higher index is to the right (higher X)
                        self._graph.add_edge(seg_a_uid, seg_b_uid, direction=Direction.RIGHT)
                        self._graph.add_edge(seg_b_uid, seg_a_uid, direction=Direction.LEFT)

                # Connect crossing segments at the same intersection
                for perp_road in sorted_perpendicular_roads:
                    perp_lanes = perp_road.forward_lanes + perp_road.backward_lanes

                    for perp_lane in perp_lanes:
                        if is_horizontal:
                            key_a = (hash(lane_a), hash(perp_lane))
                            key_b = (hash(lane_b), hash(perp_lane))
                        else:
                            key_a = (hash(perp_lane), hash(lane_a))
                            key_b = (hash(perp_lane), hash(lane_b))

                        if key_a in crossing_lookup and key_b in crossing_lookup:
                            crossing_a = crossing_lookup[key_a]
                            crossing_b = crossing_lookup[key_b]

                            if is_horizontal:
                                self._graph.add_edge(crossing_a.uid, crossing_b.uid, direction=Direction.DOWN)
                                self._graph.add_edge(crossing_b.uid, crossing_a.uid, direction=Direction.UP)
                            else:
                                self._graph.add_edge(crossing_a.uid, crossing_b.uid, direction=Direction.RIGHT)
                                self._graph.add_edge(crossing_b.uid, crossing_a.uid, direction=Direction.LEFT)

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
