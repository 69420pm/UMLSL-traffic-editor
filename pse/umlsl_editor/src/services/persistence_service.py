from __future__ import annotations

from typing import Any

from pse.umlsl_editor.src.model.domain_models.settings_model import SettingsModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import (
    TrafficSnapshotModel,
)
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import (
    TrafficSnapshotReader,
)
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_writer import (
    TrafficSnapshotWriter,
)
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import (
    UMLSLQueriesModel,
)


class PersistenceService:
    """Handles saving/loading JSON payloads for traffic snapshots and UMLSL queries."""

    VERSION = 2

    @staticmethod
    def serialize(
            snapshot: TrafficSnapshotModel,
            queries: UMLSLQueriesModel,
    ) -> dict[str, Any]:
        """
        Serialize snapshot and queries to a JSON-ready dict.

        Returns:
            Dict payload containing roads, cars, queries, and meta version.
        """
        snapshot_data = snapshot.to_dict()
        if not isinstance(snapshot_data, dict):
            raise ValueError("TrafficSnapshotModel.to_dict() must return a dict.")

        roads = snapshot_data.get("roads")
        cars = snapshot_data.get("cars")

        if roads is None or cars is None:
            raise ValueError("TrafficSnapshotModel.to_dict() must contain 'roads' and 'cars' keys.")

        queries_data = queries.to_dict()

        return {
            "meta": {"version": PersistenceService.VERSION},
            "roads": roads,
            "cars": cars,
            "queries": queries_data,
        }

    @staticmethod
    def deserialize(
            data: dict[str, Any],
            traffic_snapshot_writer: TrafficSnapshotWriter,
            traffic_snapshot_reader: TrafficSnapshotReader,
            settings_model: SettingsModel,
            umlsl_queries_model: UMLSLQueriesModel,
    ) -> None:
        """
        Populate snapshot and queries from a JSON-ready dict.

        This validates the schema minimally and ensures queries reference existing cars.
        """
        if not isinstance(data, dict):
            raise ValueError("Snapshot payload must be a JSON object.")

        meta = data.get("meta", {})
        if meta:
            if not isinstance(meta, dict):
                raise ValueError("Snapshot 'meta' must be an object.")
            version = meta.get("version", PersistenceService.VERSION)
            if version != PersistenceService.VERSION:
                raise ValueError(f"Unsupported snapshot version: {version}")

        roads = data.get("roads", [])
        cars = data.get("cars", [])
        queries = data.get("queries", [])

        if not isinstance(roads, list):
            raise ValueError("Snapshot 'roads' must be a list.")
        if not isinstance(cars, list):
            raise ValueError("Snapshot 'cars' must be a list.")
        if not isinstance(queries, list):
            raise ValueError("Snapshot 'queries' must be a list.")

        TrafficSnapshotModel.from_dict(
            {"roads": roads, "cars": cars},
            traffic_snapshot_writer,
            traffic_snapshot_reader,
            settings_model
        )

        existing_car_uids = set(traffic_snapshot_reader.get_cars().keys())
        filtered_queries: list[dict[str, Any]] = []

        for query in queries:
            if not isinstance(query, dict):
                raise ValueError("Each query must be an object.")

            assigned_car_uid = query.get("assigned_car_uid")
            if assigned_car_uid is None and "assigned_car_name" in query:
                car = traffic_snapshot_reader.get_car_by_name(query["assigned_car_name"])
                assigned_car_uid = car.uid if car else None

            if assigned_car_uid in existing_car_uids:
                normalized = dict(query)
                normalized["assigned_car_uid"] = assigned_car_uid
                filtered_queries.append(normalized)

        umlsl_queries_model.from_dict(filtered_queries)

    @staticmethod
    def serialize_external_format(
                snapshot: TrafficSnapshotModel,
        ) -> dict[str, Any]:
            """
            Serialize snapshot to the external JSON format (e.g., 'two_crossings_predefined').
            """
            snapshot_data = snapshot.to_dict()

            internal_roads = snapshot_data.get("roads", [])
            internal_cars = snapshot_data.get("cars", [])

            external_roads = []
            road_uid_to_name = {}

            for r in internal_roads:
                road_name = r.get("name", "unknown")
                road_uid_to_name[r.get("uid")] = road_name

                # Map "orientation" to "horizontal" bool, "position" to "top", and lanes to "right"/"left"
                external_roads.append({
                    "name": road_name,
                    "horizontal": r.get("orientation") == "HORIZONTAL",
                    "top": (r.get("position", 0.0) + 20) * 40,
                    "right": r.get("number_of_forward_lanes", 0),
                    "left": r.get("number_of_backward_lanes", 0)
                })

            external_cars = []
            for c in internal_cars:
                road_name = road_uid_to_name.get(c.get("road_uid"), "unknown")

                # Determine direction based on lane_index (negative index indicates backward/left lane)
                direction = "right" if c.get("lane_index", 0) >= 0 else "left"

                lane_index = c.get("lane_index", 0)
                lane = lane_index if lane_index >= 0 else abs(lane_index) - 1

                position = (c.get("position_on_lane", 0.0) + 20) * 40

                start = {
                    "road": road_name,
                    "direction": direction,
                    "lane": lane,
                    "position": position
                }

                external_cars.append({
                    "type": "NPC",
                    "start": start,
                    "speed": c.get("speed", 0.0),
                    "max_speed": c.get("speed", 0.0),
                    "first_goal": start
                })

            return {
                "name": "TEST",
                "scenario_name": "test",
                "players": len(external_cars),
                "roads": external_roads,
                "cars": external_cars
            }

    @staticmethod
    def deserialize_external_format(
                data: dict[str, Any],
                traffic_snapshot_writer: TrafficSnapshotWriter,
                traffic_snapshot_reader: TrafficSnapshotReader,
                settings_model: SettingsModel
        ) -> None:
            """
            Populate snapshot from the external JSON format.
            """
            import uuid

            ext_roads = data.get("roads", [])
            ext_cars = data.get("cars", [])

            internal_roads = []
            road_name_to_uid = {}

            for r in ext_roads:
                road_uid = str(uuid.uuid4())
                road_name = r.get("name", "")
                road_name_to_uid[road_name] = road_uid

                # Map "horizontal" to "HORIZONTAL"/"VERTICAL", "top" to "position", and "right"/"left" to lanes
                internal_roads.append({
                    "uid": road_uid,
                    "name": road_name,
                    "orientation": "HORIZONTAL" if r.get("horizontal") else "VERTICAL",
                    "position": r.get("top", 0.0),
                    "number_of_forward_lanes": r.get("right", 0),
                    "number_of_backward_lanes": r.get("left", 0)
                })

            internal_cars = []
            for idx, c in enumerate(ext_cars):
                start = c.get("start", {})
                road_name = start.get("road", "")
                direction = start.get("direction", "right")
                lane_val = start.get("lane", 0)

                # Reconstruct lane_index based on direction
                lane_index = lane_val if direction in ["right", "down"] else -lane_val

                internal_cars.append({
                    "uid": str(uuid.uuid4()),
                    "name": f"C{idx+1}",
                    "road_uid": road_name_to_uid.get(road_name, ""),
                    "lane_index": lane_index,
                    "position_on_lane": c.get("loc", 0.0),
                    "transition": 0.0,
                    "speed": c.get("speed", 0.0),
                    "length": 1,
                    "color": "lightblue",
                    "acceleration": 1.0,
                    "next_turn": None
                })

            TrafficSnapshotModel.from_dict(
                {"roads": internal_roads, "cars": internal_cars},
                traffic_snapshot_writer,
                traffic_snapshot_reader,
                settings_model
            )
