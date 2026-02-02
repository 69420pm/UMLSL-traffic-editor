from typing import Any

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_validator import TrafficSnapshotValidator
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import TrafficSnapshotWriter
from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.model.helper.directional_graph import Direction, DirectionalGraph
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

    def get_cars(self) -> list[Car]:
        pass

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
        if road.orientation == RoadOrientation.HORIZONTAL:
            tail_position = tail_x
        else:
            tail_position = tail_y

        # Get sorted perpendicular road positions to determine segment boundaries
        if road.orientation == RoadOrientation.HORIZONTAL:
            perpendicular_roads = sorted(self._vertical_roads.values(), key=lambda r: r.position)
        else:
            perpendicular_roads = sorted(self._horizontal_roads.values(), key=lambda r: r.position)

        # Segments are ordered: lane_segment, crossing, lane_segment, crossing, ..., lane_segment
        # The boundaries are at the perpendicular road positions

        # Find which segment contains the tail position
        for i, segment_uid in enumerate(segment_uids):
            segment = self._segments[segment_uid]

            if segment.is_lane_segment:
                # Lane segment - determine its boundaries
                # Lane segments alternate with crossing segments
                # Index 0 is before first crossing, index 2 is between crossing 0 and 1, etc.
                lane_segment_index = i // 2  # 0, 1, 2, ... for lane segments at positions 0, 2, 4, ...

                if lane_segment_index == 0:
                    # First lane segment: from -inf to first perpendicular road
                    left_bound = float('-inf')
                    if perpendicular_roads:
                        right_bound = perpendicular_roads[0].position
                    else:
                        right_bound = float('inf')
                elif lane_segment_index > len(perpendicular_roads):
                    # Last lane segment: from last perpendicular road to +inf
                    left_bound = perpendicular_roads[-1].position + self.lane_width
                    right_bound = float('inf')
                else:
                    # Middle lane segment: between two perpendicular roads
                    left_bound = perpendicular_roads[lane_segment_index - 1].position + self.lane_width
                    right_bound = perpendicular_roads[lane_segment_index].position

                if left_bound <= tail_position < right_bound:
                    return segment
            else:
                # Crossing segment - its boundaries are defined by the perpendicular road
                crossing_index = i // 2  # 0, 1, 2, ... for crossings at positions 1, 3, 5, ...
                if crossing_index < len(perpendicular_roads):
                    perp_road = perpendicular_roads[crossing_index]
                    left_bound = perp_road.position
                    right_bound = perp_road.position + self.lane_width

                    if left_bound <= tail_position < right_bound:
                        return segment

        # If we reach here, the tail is in the last segment (could be at +inf boundary)
        return self._segments[segment_uids[-1]]

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
        self._graph = DirectionalGraph()

        # Sort roads by position for consistent ordering
        sorted_horizontal_roads = sorted(self._horizontal_roads.values(), key=lambda r: r.position)
        sorted_vertical_roads = sorted(self._vertical_roads.values(), key=lambda r: r.position)

        # Collect all lanes
        horizontal_lanes: list[Lane] = []
        vertical_lanes: list[Lane] = []

        for road in sorted_horizontal_roads:
            # Add lanes in order from lowest index to highest (backward lanes then forward)
            all_lanes = sorted(road.backward_lanes + road.forward_lanes, key=lambda l: l.lane_index)
            horizontal_lanes.extend(all_lanes)

        for road in sorted_vertical_roads:
            all_lanes = sorted(road.backward_lanes + road.forward_lanes, key=lambda l: l.lane_index)
            vertical_lanes.extend(all_lanes)

        # Phase 1: Create all crossing segments
        # crossing_map[(h_lane_hash, v_lane_hash)] = CrossingSegment
        crossing_map: dict[tuple[int, int], CrossingSegment] = {}

        for h_lane in horizontal_lanes:
            for v_lane in vertical_lanes:
                crossing = CrossingSegment(horizontal_lane=h_lane, vertical_lane=v_lane)
                self._segments[crossing.uid] = crossing
                crossing_map[(hash(h_lane), hash(v_lane))] = crossing
                self._graph.add_node(crossing.uid)

        # Phase 2: Create lane segments and build _segments_by_lane
        # For each horizontal lane: segments go left to right (increasing x)
        # Order: lane_seg, crossing, lane_seg, crossing, ..., lane_seg

        for h_lane in horizontal_lanes:
            lane_hash = hash(h_lane)
            segment_uids: list[str] = []

            # Create lane segments between/around crossings
            # Number of lane segments = number of vertical roads + 1
            num_lane_segments = len(sorted_vertical_roads) + 1
            lane_segments: list[LaneSegment] = []

            for _ in range(num_lane_segments):
                ls = LaneSegment(lane=h_lane)
                self._segments[ls.uid] = ls
                self._graph.add_node(ls.uid)
                lane_segments.append(ls)

            # Build ordered segment list and connect horizontally (LEFT/RIGHT)
            for i, v_road in enumerate(sorted_vertical_roads):
                # Lane segment before this crossing
                segment_uids.append(lane_segments[i].uid)

                # Get the crossing for this horizontal lane and any vertical lane on this road
                # We need the crossing at this vertical road position
                v_lane = (v_road.backward_lanes + v_road.forward_lanes)[0]  # Any lane to find crossings
                # Actually we need the crossing for h_lane with each v_lane on this road
                # But for the horizontal lane's segment list, we need crossings with vertical lanes

                # Get all vertical lanes on this road, sorted by index
                v_road_lanes = sorted(v_road.backward_lanes + v_road.forward_lanes, key=lambda l: l.lane_index)

                # Add crossings for all vertical lanes on this road
                for v_lane in v_road_lanes:
                    crossing = crossing_map[(hash(h_lane), hash(v_lane))]
                    segment_uids.append(crossing.uid)

                # Connect lane segment to first crossing on the right
                first_v_lane = v_road_lanes[0]
                first_crossing = crossing_map[(hash(h_lane), hash(first_v_lane))]
                self._graph.add_edge(lane_segments[i].uid, first_crossing.uid, Direction.RIGHT)

                # Connect last crossing to next lane segment on the right
                last_v_lane = v_road_lanes[-1]
                last_crossing = crossing_map[(hash(h_lane), hash(last_v_lane))]
                self._graph.add_edge(last_crossing.uid, lane_segments[i + 1].uid, Direction.RIGHT)

            # Add the last lane segment
            segment_uids.append(lane_segments[-1].uid)

            self._segments_by_lane[lane_hash] = segment_uids

        # For each vertical lane: segments go top to bottom (increasing y)
        for v_lane in vertical_lanes:
            lane_hash = hash(v_lane)
            segment_uids: list[str] = []

            num_lane_segments = len(sorted_horizontal_roads) + 1
            lane_segments: list[LaneSegment] = []

            for _ in range(num_lane_segments):
                ls = LaneSegment(lane=v_lane)
                self._segments[ls.uid] = ls
                self._graph.add_node(ls.uid)
                lane_segments.append(ls)

            for i, h_road in enumerate(sorted_horizontal_roads):
                segment_uids.append(lane_segments[i].uid)

                h_road_lanes = sorted(h_road.backward_lanes + h_road.forward_lanes, key=lambda l: l.lane_index)

                for h_lane in h_road_lanes:
                    crossing = crossing_map[(hash(h_lane), hash(v_lane))]
                    segment_uids.append(crossing.uid)

                # Connect lane segment to first crossing below (DOWN direction)
                first_h_lane = h_road_lanes[0]
                first_crossing = crossing_map[(hash(first_h_lane), hash(v_lane))]
                self._graph.add_edge(lane_segments[i].uid, first_crossing.uid, Direction.DOWN)

                # Connect last crossing to next lane segment below
                last_h_lane = h_road_lanes[-1]
                last_crossing = crossing_map[(hash(last_h_lane), hash(v_lane))]
                self._graph.add_edge(last_crossing.uid, lane_segments[i + 1].uid, Direction.DOWN)

            segment_uids.append(lane_segments[-1].uid)

            self._segments_by_lane[lane_hash] = segment_uids

        # Phase 3: Connect crossing segments to adjacent crossings (within same road intersection)
        # Crossings on adjacent horizontal lanes (same vertical road) connect UP/DOWN
        # Crossings on adjacent vertical lanes (same horizontal road) connect LEFT/RIGHT

        for v_road in sorted_vertical_roads:
            v_road_lanes = sorted(v_road.backward_lanes + v_road.forward_lanes, key=lambda l: l.lane_index)

            for h_lane in horizontal_lanes:
                # Connect adjacent crossings along vertical direction (different v_lanes, same h_lane)
                for j in range(len(v_road_lanes) - 1):
                    v_lane_curr = v_road_lanes[j]
                    v_lane_next = v_road_lanes[j + 1]
                    crossing_curr = crossing_map[(hash(h_lane), hash(v_lane_curr))]
                    crossing_next = crossing_map[(hash(h_lane), hash(v_lane_next))]
                    self._graph.add_edge(crossing_curr.uid, crossing_next.uid, Direction.RIGHT)

        for h_road in sorted_horizontal_roads:
            h_road_lanes = sorted(h_road.backward_lanes + h_road.forward_lanes, key=lambda l: l.lane_index)

            for v_lane in vertical_lanes:
                # Connect adjacent crossings along horizontal direction (different h_lanes, same v_lane)
                for j in range(len(h_road_lanes) - 1):
                    h_lane_curr = h_road_lanes[j]
                    h_lane_next = h_road_lanes[j + 1]
                    crossing_curr = crossing_map[(hash(h_lane_curr), hash(v_lane))]
                    crossing_next = crossing_map[(hash(h_lane_next), hash(v_lane))]
                    self._graph.add_edge(crossing_curr.uid, crossing_next.uid, Direction.DOWN)

        # Phase 4: Connect parallel lane segments (adjacent lanes in same direction or across directions)
        # For horizontal lanes: parallel lane segments connect UP/DOWN
        for i in range(len(horizontal_lanes) - 1):
            h_lane_curr = horizontal_lanes[i]
            h_lane_next = horizontal_lanes[i + 1]

            curr_segments = self._segments_by_lane[hash(h_lane_curr)]
            next_segments = self._segments_by_lane[hash(h_lane_next)]

            # Get only the lane segments (not crossings) - they are at even indices
            curr_lane_seg_uids = [uid for uid in curr_segments if self._segments[uid].is_lane_segment]
            next_lane_seg_uids = [uid for uid in next_segments if self._segments[uid].is_lane_segment]

            # Connect corresponding lane segments
            for curr_uid, next_uid in zip(curr_lane_seg_uids, next_lane_seg_uids):
                self._graph.add_edge(curr_uid, next_uid, Direction.DOWN)

        # For vertical lanes: parallel lane segments connect LEFT/RIGHT
        for i in range(len(vertical_lanes) - 1):
            v_lane_curr = vertical_lanes[i]
            v_lane_next = vertical_lanes[i + 1]

            curr_segments = self._segments_by_lane[hash(v_lane_curr)]
            next_segments = self._segments_by_lane[hash(v_lane_next)]

            curr_lane_seg_uids = [uid for uid in curr_segments if self._segments[uid].is_lane_segment]
            next_lane_seg_uids = [uid for uid in next_segments if self._segments[uid].is_lane_segment]

            for curr_uid, next_uid in zip(curr_lane_seg_uids, next_lane_seg_uids):
                self._graph.add_edge(curr_uid, next_uid, Direction.RIGHT)

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
