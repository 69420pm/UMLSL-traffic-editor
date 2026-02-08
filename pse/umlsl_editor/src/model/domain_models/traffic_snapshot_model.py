import json
from typing import Any

import networkx as nx

from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import (
    TrafficSnapshotReader,
)
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_validator import (
    TrafficSnapshotValidator,
)
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import (
    TrafficSnapshotWriter,
)
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel
from pse.umlsl_editor.src.model.entities.car import Car, CarParams
from pse.umlsl_editor.src.model.entities.road import Road, RoadOrientation, RoadParams
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQueryParams
from pse.umlsl_editor.src.model.helper.directional_graph import Direction
from pse.umlsl_editor.src.model.helper.event_types import TrafficSnapshotEventType
from pse.umlsl_editor.src.model.helper.observables import (
    Observable,
    ObservableDict,
    ReadOnlyMergedDictView,
)
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.crossing_segment import (
    CrossingSegment,
)
from pse.umlsl_editor.src.model.traffic_value_objects.segments.lane_segment import (
    LaneSegment,
)
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnDirection, TurnIntent
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

    def get_valid_turn_intent_lanes(self, car_position: float, car_speed: float, car_lane: Lane, car_length: float,
                                    turn_direction: TurnDirection) -> list[Lane]:
        if car_speed < 0 or turn_direction not in [TurnDirection.LEFT, TurnDirection.RIGHT]:
            return []

        road_of_lane = self.get_road_by_uid(car_lane.road_uid)
        if road_of_lane is None:
            raise ValueError(f"Road with uid {car_lane.road_uid} not found.")

        if road_of_lane.orientation == RoadOrientation.HORIZONTAL:
            direction = Direction.RIGHT if car_lane.lane_index >= 0 else Direction.LEFT
        else:
            direction = Direction.UP if car_lane.lane_index >= 0 else Direction.DOWN

        segment = self.get_segment_from_lane_position(car_lane, car_position)

        if segment is None:
            return []

        lanes_to_turn_into: list[Lane] = []
        current_segment_uid = segment.uid
        adjacent_segment = self.get_adjacent_segment(current_segment_uid, direction)
        while isinstance(adjacent_segment, CrossingSegment):
            lane_to_turn_into = adjacent_segment.horizontal_lane if road_of_lane.orientation == RoadOrientation.VERTICAL else adjacent_segment.vertical_lane

            # go through all 4 casees
            if road_of_lane.orientation == RoadOrientation.HORIZONTAL:
                if turn_direction == TurnDirection.LEFT:
                    # lane indeces must be different
                    if (car_lane.lane_index >= 0 and lane_to_turn_into.lane_index >= 0) or (
                            car_lane.lane_index < 0 and lane_to_turn_into.lane_index < 0):
                        lanes_to_turn_into.append(lane_to_turn_into)
                elif turn_direction == TurnDirection.RIGHT:
                    # lane indeces must be the same
                    if (car_lane.lane_index >= 0 and lane_to_turn_into.lane_index < 0) or (
                            car_lane.lane_index < 0 and lane_to_turn_into.lane_index >= 0):
                        lanes_to_turn_into.append(lane_to_turn_into)
            if road_of_lane.orientation == RoadOrientation.VERTICAL:
                if turn_direction == TurnDirection.LEFT:
                    # lane indeces must be different
                    if (car_lane.lane_index >= 0 and lane_to_turn_into.lane_index < 0) or (
                            car_lane.lane_index < 0 and lane_to_turn_into.lane_index >= 0):
                        lanes_to_turn_into.append(lane_to_turn_into)
                elif turn_direction == TurnDirection.RIGHT:
                    # lane indeces must be the same
                    if (car_lane.lane_index >= 0 and lane_to_turn_into.lane_index >= 0) or (
                            car_lane.lane_index < 0 and lane_to_turn_into.lane_index < 0):
                        lanes_to_turn_into.append(lane_to_turn_into)
            adjacent_segment = self.get_adjacent_segment(adjacent_segment.uid, direction)

        return lanes_to_turn_into

    def get_scene_size(self) -> float:
        return self.screen_size

    def is_road_existing(self, uid: str) -> bool:
        if uid in self._horizontal_roads or uid in self._vertical_roads:
            return True
        return False

    def is_car_existing(self, uid: str) -> bool:
        return uid in self._cars

    def validate_road_params(self, road_params: RoadParams, new_instantiation: bool,
                             road_uid: str | None = None) -> None:
        if not new_instantiation and road_uid is None or new_instantiation and road_uid is not None:
            raise ValueError('road_uid must be None for new road instantiation.')
        self.validator.validate_road_params(road_params, new_instantiation, road_uid)

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
            queries_model: UMLSLQueriesModel,
            settings_model: SettingsModel,
            cars: ObservableDict[str, Car] | None = None,
    ):

        super().__init__()
        self._cars = cars if cars is not None else ObservableDict[str, Car](
            on_add=self._on_car_added,
            on_remove=self._on_car_removed,
            on_update=self._on_car_updated
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
        self._debug_segments: dict[str, Segment] = {}
        """Dictionary of segments, keyed by their uid."""
        # self._connections: dict[str, dict[Direction, str]] = {}
        # """Dictionary of segment connections, keyed by segment uid. And in the direction dict all connected segments uids."""
        self._segments_by_lane: dict[Lane, list[str]] = {}
        """Dictionary mapping the lane to their corresponding segment uids."""
        self._graph = nx.DiGraph()
        """Graph representing the connectivity of segments."""

        self._read_only_roads = ReadOnlyMergedDictView([self._horizontal_roads, self._vertical_roads])
        """Read-only view of the roads dictionary."""
        self._read_only_cars = ReadOnlyMergedDictView([self._cars])
        """Read-only view of the cars dictionary."""

        self.lane_width = DIMENSION.LANE_WIDTH
        self.screen_size = (DIMENSION.SCENE_SIZE + 100) / 2

        self.validator = TrafficSnapshotValidator(self)
        self._queries_model: UMLSLQueriesModel = queries_model
        self.settings_model: SettingsModel = settings_model

    @property
    def cars(self):
        return self._read_only_cars

    @property
    def roads(self):
        return self._read_only_roads

    def _on_car_added(self, car: Car):
        self.notify(TrafficSnapshotEventType.CAR_ADDED, car)
        self._revalidate_queries()

    def _on_car_removed(self, car: Car):
        self.notify(TrafficSnapshotEventType.CAR_REMOVED, car)
        self._revalidate_queries()

    def _on_car_updated(self, car: Car):
        self.notify(TrafficSnapshotEventType.CAR_UPDATED, car)
        self._revalidate_queries()

    def _on_road_added(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_ADDED, road)
        self._recalculate_static_segments()
        self._revalidate_queries()

    def _on_road_removed(self, road: Road):
        # Recalculate segments BEFORE notifying observers to ensure consistency.
        # This prevents observers from accessing stale segments that reference the removed road.
        self._recalculate_static_segments()
        self.notify(TrafficSnapshotEventType.ROAD_REMOVED, road)
        self._revalidate_queries()

    def _on_road_updated(self, road: Road):
        self.notify(TrafficSnapshotEventType.ROAD_UPDATED, road)
        self._recalculate_static_segments()
        self._revalidate_queries()

    def get_cars_on_road(self, road: Road) -> list[Car]:
        return [car for car in self._cars.values() if car.lane.road_uid == road.uid]

    def get_cars(self) -> dict[str, Car]:
        return dict(self._read_only_cars)

    def get_car_list(self) -> list[Car]:
        return list(self._cars.values())

    def get_car_by_name(self, name: str) -> Car | None:
        for car in self._cars.values():
            if car.name == name:
                return car
        return None

    def get_roads(self) -> dict[str, Road]:
        return {**self._horizontal_roads, **self._vertical_roads}

    def get_cars_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Car]:
        pass

    def get_roads_in_rectangle(self, x_min: float, y_min: float, x_max: float, y_max: float) -> list[Road]:
        pass

    def validate_lane(self, road: Road, lane_index: int, lane_direction: str) -> bool:
        pass

    def add_road(self, road: Road) -> None:
        if road.orientation == RoadOrientation.HORIZONTAL:
            self._horizontal_roads[road.uid] = road
        else:
            self._vertical_roads[road.uid] = road
        self._revalidate_cars()

    def remove_road(self, road_uid: str) -> None:
        if road_uid in self._horizontal_roads:
            self._horizontal_roads.pop(road_uid)
        elif road_uid in self._vertical_roads:
            self._vertical_roads.pop(road_uid)

        self._revalidate_cars()

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
        self._revalidate_cars()

    def add_car(self, car: Car) -> None:
        self._cars[car.uid] = car

    def remove_car(self, car_uid: str) -> None:
        self._cars.pop(car_uid)

    def update_car_with_params(self, car_uid: str, car_params: CarParams) -> None:
        car = self._cars.get(car_uid)
        car.update_from_params(car_params, self, self.settings_model)
        self._cars[car_uid] = car

    def get_segment_from_lane_position(self, lane: Lane, position_on_lane: float) -> Segment | None:
        segment_uids = self._segments_by_lane.get(lane)
        if segment_uids is None:
            return None

        segments: list[Segment] = []
        for seg_uid in segment_uids:
            segments.append(self._segments[seg_uid])

        road = self.get_road_by_uid(lane.road_uid)
        coord_index = 0 if road.orientation == RoadOrientation.HORIZONTAL else 1
        segments.sort(key=lambda s: s.get_position(self)[coord_index])
        if road.orientation == RoadOrientation.VERTICAL:
            segments.reverse()

        first_segment_on_road = segments[0]
        previous_segment: Segment | None = first_segment_on_road
        for segment in segments:
            seg_pos_on_lane = segment.get_position(self)[coord_index]
            if road.orientation == RoadOrientation.HORIZONTAL:
                if seg_pos_on_lane < position_on_lane:
                    previous_segment = segment
                else:
                    return previous_segment
            if road.orientation == RoadOrientation.VERTICAL:
                if seg_pos_on_lane > position_on_lane:
                    previous_segment = segment
                else:
                    return previous_segment

        return previous_segment

    def all_segments(self) -> list[Segment]:
        segments = []
        for segment in self._segments.values():
            segments.append(segment)

        return segments

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
            # Sort Bottom to Top (low y to high y) based on physical lane position
            h_lanes.sort(key=lambda l: l.get_one_dimensional_position(self))

            lane_physical_segments: dict[Lane, list[Segment]] = {}

            for lane in h_lanes:
                segments = []
                # Left Inf
                left_inf = LaneSegment(lane=lane)
                self._segments[left_inf.uid] = left_inf
                segments.append(left_inf)

                for v_road in vertical_roads:
                    v_lanes = sorted(
                        v_road.forward_lanes + v_road.backward_lanes,
                        key=lambda l: l.get_one_dimensional_position(self)
                    )
                    for v_lane in v_lanes:
                        segments.append(crossing_map[(lane, v_lane)])

                    mid_seg = LaneSegment(lane=lane)
                    self._segments[mid_seg.uid] = mid_seg
                    segments.append(mid_seg)

                lane_physical_segments[lane] = segments

                # Store spatial order (low x to high x)
                segments_uids = [s.uid for s in segments]
                self._segments_by_lane[lane] = segments_uids

                # Flow Direction Setup
                if lane.lane_index >= 0:
                    flow_uids = segments_uids
                    flow_dir = Direction.RIGHT
                else:
                    flow_uids = list(reversed(segments_uids))
                    flow_dir = Direction.LEFT

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
                        self._graph.add_edge(s_t.uid, s_b.uid, direction=Direction.UP)
                        self._graph.add_edge(s_b.uid, s_t.uid, direction=Direction.DOWN)

        # 3. Process Vertical Roads
        for v_road in vertical_roads:
            v_lanes = v_road.forward_lanes + v_road.backward_lanes
            # Sort Left to Right (low x to high x) based on physical lane position
            v_lanes.sort(key=lambda l: l.get_one_dimensional_position(self))

            lane_physical_segments: dict[Lane, list[Segment]] = {}

            for lane in v_lanes:
                segments = []
                # Bottom Inf
                top_inf = LaneSegment(lane=lane)
                self._segments[top_inf.uid] = top_inf
                segments.append(top_inf)

                for h_road in horizontal_roads:
                    h_lanes = sorted(
                        h_road.forward_lanes + h_road.backward_lanes,
                        key=lambda l: l.get_one_dimensional_position(self)
                    )
                    for h_lane in h_lanes:
                        segments.append(crossing_map[(h_lane, lane)])

                    mid_seg = LaneSegment(lane=lane)
                    self._segments[mid_seg.uid] = mid_seg
                    segments.append(mid_seg)

                lane_physical_segments[lane] = segments

                # Store spatial order (low y to high y)
                segments_uids = [s.uid for s in segments]
                self._segments_by_lane[lane] = segments_uids

                # Flow Direction Setup
                if lane.lane_index >= 0:
                    flow_uids = segments_uids
                    flow_dir = Direction.UP
                else:
                    flow_uids = list(reversed(segments_uids))
                    flow_dir = Direction.DOWN

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

    def print_graph(self) -> None:
        """
        Prints the graph structure to stdout for debugging purposes.
        Shows segments and their outgoing connections with directions.
        """
        print("=== Traffic Graph Structure ===")
        for segment_uid in self._graph.nodes:
            segment_info = self.get_segment_info(segment_uid, True)
            print(f"\n[Segment] {segment_info}")

            # Print outgoing connections
            out_edges = self._graph.out_edges(segment_uid, data=True)
            if not out_edges:
                print("  -> (no outgoing connections)")
            else:
                for _, target_uid, data in out_edges:
                    direction = data.get('direction')
                    direction_name = direction.name if direction else "UNKNOWN"
                    target_info = self.get_segment_info(target_uid)
                    print(f"  -> [{direction_name}] to {target_info}")
        print("===============================")

    def get_segment_info(self, segment_uid: str, include_uid: bool = False) -> str:
        # todo: use polymorphism to remove instance checks
        segment = self._segments.get(segment_uid)
        if segment is None:
            return f"unknown segment with uid {segment_uid}"

        def format_lane(lane: Lane) -> str:
            actual_index = lane.lane_index + 1 if lane.lane_index >= 0 else -lane.lane_index
            prefix = "f" if lane.lane_index >= 0 else "b"
            road_uid = f"({lane.road_uid})" if include_uid else ""
            return f"{prefix}{actual_index}{road_uid}"

        uid_suffix = f"({segment.uid})" if include_uid else ""
        if isinstance(segment, CrossingSegment):
            h_road = self.get_road_by_uid(segment.horizontal_lane.road_uid)
            v_road = self.get_road_by_uid(segment.vertical_lane.road_uid)
            return (f"crossing{uid_suffix} "
                    f"at R{h_road.name}({format_lane(segment.horizontal_lane)}) x "
                    f"R{v_road.name}({format_lane(segment.vertical_lane)})")

        elif isinstance(segment, LaneSegment):
            road = self.get_road_by_uid(segment.lane.road_uid)
            return (f"lane{uid_suffix} "
                    f"at R{road.name}({format_lane(segment.lane)})")

        raise NotImplementedError(f"Unknown segment type: {type(segment)}")

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the TrafficSnapshot instance to a dictionary suitable for JSON encoding.
        """
        roads_data: list[dict[str, Any]] = []
        for road in self.get_roads().values():
            roads_data.append({
                "uid": road.uid,
                "name": road.name,
                "orientation": road.orientation.name,
                "position": road.position,
                "number_of_forward_lanes": road.number_of_forward_lanes,
                "number_of_backward_lanes": road.number_of_backward_lanes,
            })

        cars_data: list[dict[str, Any]] = []
        for car in self.get_car_list():
            car_payload: dict[str, Any] = {
                "uid": car.uid,
                "name": car.name,
                "road_uid": car.lane.road_uid,
                "lane_index": car.lane.lane_index,
                "position_on_lane": car.position_on_lane,
                "transition": car.transition,
                "speed": car.speed,
                "length": car.length,
                "color": car.color,
                "acceleration": car.acceleration,
            }

            if car.next_turn is not None:
                car_payload["next_turn"] = {
                    "direction": car.next_turn.direction.name,
                    "target_lane": {
                        "road_uid": car.next_turn.target_lane.road_uid,
                        "lane_index": car.next_turn.target_lane.lane_index,
                    },
                }
            else:
                car_payload["next_turn"] = None

            cars_data.append(car_payload)

        return {"roads": roads_data, "cars": cars_data}

    def to_json(self) -> str:
        """
        Serializes the TrafficSnapshot instance to a JSON string.
        """
        return json.dumps(self.to_dict(), indent=2)

    def debug_get_segments(self) -> dict[str, Segment]:
        return self._debug_segments

    @staticmethod
    def from_dict(
            data: dict[str, Any],
            writer: TrafficSnapshotWriter,
            reader: TrafficSnapshotReader,
            settings_model: SettingsModel
    ) -> "TrafficSnapshotModel":
        """
        Creates a TrafficSnapshot instance from a dictionary.

        Args:
            data: A dictionary containing 'roads' and 'cars' keys.
            writer: A TrafficSnapshotWriter instance.
            reader: A TrafficSnapshotReader instance.
        """
        if not isinstance(data, dict):
            raise ValueError("Traffic snapshot data must be a dictionary.")

        roads_data = data.get("roads", [])
        cars_data = data.get("cars", [])

        if not isinstance(roads_data, list):
            raise ValueError("Traffic snapshot 'roads' must be a list.")
        if not isinstance(cars_data, list):
            raise ValueError("Traffic snapshot 'cars' must be a list.")

        for road_data in roads_data:
            if not isinstance(road_data, dict):
                raise ValueError("Each road must be a dictionary.")

            orientation_raw = road_data.get("orientation")
            if isinstance(orientation_raw, RoadOrientation):
                orientation = orientation_raw
            elif isinstance(orientation_raw, str):
                orientation = RoadOrientation[orientation_raw]
            else:
                orientation = RoadOrientation(orientation_raw)

            road_params = RoadParams(
                name=road_data["name"],
                orientation=orientation,
                position=road_data["position"],
                number_of_forward_lanes=road_data["number_of_forward_lanes"],
                number_of_backward_lanes=road_data["number_of_backward_lanes"],
            )
            reader.validate_road_params(road_params, True)

            road_uid = road_data.get("uid")
            if not road_uid:
                raise ValueError("Road uid is required.")
            forward_lanes = [
                Lane(lane_index=i, road_uid=road_uid)
                for i in range(road_params.number_of_forward_lanes)
            ]
            backward_lanes = [
                Lane(lane_index=-(i + 1), road_uid=road_uid)
                for i in range(road_params.number_of_backward_lanes)
            ]
            road = Road(
                uid=road_uid,
                name=road_params.name,
                orientation=road_params.orientation,
                position=road_params.position,
                number_of_forward_lanes=road_params.number_of_forward_lanes,
                number_of_backward_lanes=road_params.number_of_backward_lanes,
                forward_lanes=forward_lanes,
                backward_lanes=backward_lanes,
            )

            writer.add_road(road)

        for car_data in cars_data:
            if not isinstance(car_data, dict):
                raise ValueError("Each car must be a dictionary.")

            lane = Lane(
                road_uid=car_data["road_uid"],
                lane_index=car_data["lane_index"],
            )

            next_turn_data = car_data.get("next_turn")
            next_turn = None
            if isinstance(next_turn_data, dict):
                direction_raw = next_turn_data.get("direction")
                if isinstance(direction_raw, TurnDirection):
                    direction = direction_raw
                elif isinstance(direction_raw, str):
                    direction = TurnDirection[direction_raw]
                else:
                    direction = TurnDirection(direction_raw)

                target_lane_data = next_turn_data.get("target_lane", {})
                if isinstance(target_lane_data,
                              dict) and "road_uid" in target_lane_data and "lane_index" in target_lane_data:
                    target_lane = Lane(
                        road_uid=target_lane_data["road_uid"],
                        lane_index=target_lane_data["lane_index"],
                    )
                    next_turn = TurnIntent(direction=direction, target_lane=target_lane)

            car_params = CarParams(
                name=car_data["name"],
                lane=lane,
                color=car_data["color"],
                position_on_lane=car_data["position_on_lane"],
                transition=car_data.get("transition", 0.0),
                speed=car_data["speed"],
                length=car_data["length"],
                next_turn=next_turn,
                acceleration=car_data.get("acceleration", 0.0),
            )
            reader.validate_car_params(car_params, True)

            car = Car.from_params(car_params, reader, settings_model)
            car_uid = car_data.get("uid")
            if not car_uid:
                raise ValueError("Car uid is required.")
            car.uid = car_uid
            writer.add_car(car)

        return writer if isinstance(writer, TrafficSnapshotModel) else None

    @classmethod
    def from_json(cls, json_string: str, settings_model: SettingsModel) -> "TrafficSnapshotModel":
        """
        Creates a TrafficSnapshot instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing traffic snapshot data.
            settings_model: A SettingsModel instance for validation during deserialization.

        """
        data = json.loads(json_string)
        snapshot = cls()
        cls.from_dict(data, snapshot, snapshot, settings_model)
        return snapshot

    def print_segments_by_lane(self):
        for lane, segment_uids in self._segments_by_lane.items():
            road = self.get_road_by_uid(lane.road_uid)
            print(f"Lane {lane.lane_index} on Road {road.name} has segments:")
            for uid in segment_uids:
                segment = self._segments[uid]
                position = segment.get_position(self)
                size = segment.get_size(self)
                print(f"  - {segment.uid}: {type(segment).__name__}, position={position}, size={size}")
        pass

    def _revalidate_cars(self):
        cars_to_remove = []
        for car in self._cars.values():
            if not self.validator.validate_car_and_autocorrect(car):
                cars_to_remove.append(car)

        for car in cars_to_remove:
            self.remove_car(car.uid)

    def _revalidate_queries(self):
        from pse.umlsl_editor.src.query.evaluator import UMLSLEvaluator
        self.validator.validate_queries(self._queries_model)
        umlsl_evaluator = UMLSLEvaluator(self)
        for query in self._queries_model.queries.values():
            car = self._cars.get(query.assigned_car_uid)
            holding = umlsl_evaluator.evaluate_query(query.latex, car).holds
            new_query_params = UMLSLQueryParams(latex=query.latex,
                                                validation=holding,
                                                assigned_car_uid=car.uid)
            self._queries_model.update_umlsl_query(query, new_query_params)
