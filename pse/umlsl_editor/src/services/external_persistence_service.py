import uuid
from typing import Any

from PIL import ImageColor

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


class ExternalPersistenceService:
    """Handles saving/loading JSON payloads to and from external program formats."""

    @staticmethod
    def serialize(
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
        road_uid_to_orientation = {}
        road_uid_to_right_lanes = {}

        for r in internal_roads:
            road_name = r.get("name", "unknown")
            road_uid_to_name[r.get("uid")] = road_name

            orientation = r.get("orientation") == "HORIZONTAL"
            road_uid_to_orientation[r.get("uid")] = orientation

            offset = 12 if orientation else 20

            top = r.get("position", 0.0) + offset
            right = r.get("number_of_forward_lanes", 0)
            left = r.get("number_of_backward_lanes", 0)

            road_uid_to_right_lanes[r.get("uid")] = right



            if orientation:
                top -= right
            else:
                (right, left) = (left, right)
                top -= left


            # Map "orientation" to "horizontal" bool, "position" to "top", and lanes to "right"/"left"
            external_roads.append(
                {
                    "name": road_name,
                    "horizontal": orientation,
                    "top": top * 40,
                    "right": r.get("number_of_forward_lanes", 0),
                    "left": r.get("number_of_backward_lanes", 0),
                }
            )

        if not any(r.get("name") in ["bottom", "right", "top", "left"] for r in external_roads):
            border_roads = [
                {"name": "bottom", "horizontal": True, "top": 0, "right": 1, "left": 0},
                {"name": "right", "horizontal": False, "top": 1560, "right": 0, "left": 1},
                {"name": "top", "horizontal": True, "top": 920, "right": 0, "left": 1},
                {"name": "left", "horizontal": False, "top": 0, "right": 1, "left": 0},
            ]
            external_roads.extend(border_roads)

        external_cars = []
        for c in internal_cars:
            road_name = road_uid_to_name.get(c.get("road_uid"), "unknown")



            lane_index = c.get("lane_index", 0)
            lane = lane_index if lane_index >= 0 else abs(lane_index) - 1

            if c.get("road"):
                pass

            offset = 20 if road_uid_to_orientation.get(c.get("road_uid")) else 12
            position = (c.get("position_on_lane", 0.0) + offset) * 40

            # Determine direction based on lane_index (negative index indicates backward/left lane)
            direction = "right" if c.get("lane_index", 0) >= 0 else "left"
            if not road_uid_to_orientation.get(c.get("road_uid")):
                direction = "right" if direction == "left" else "left"

            # switch lane index for roads with direction "right" (so lane 0 to lane 2 becomes lane 2 to lane 0)
            if direction == "right":
                # get the number of right lanes for the road that this car is on
                num_of_right_lanes = road_uid_to_right_lanes.get(c.get("road_uid"))
                # switch lane index for roads with direction "right"
                lane = num_of_right_lanes - lane - 1

            color = ImageColor.getrgb(c.get("color", "green"))

            start = {
                "road": road_name,
                "direction": direction,
                "lane": lane,
                "position": position
            }

            external_cars.append({
                "type": "NPC",
                "name": c.get("name", ""),
                "start": start,
                "first_goal": start,
                "color": color,
                "size": c.get("length", 1.0)*40,
                "speed": c.get("speed", 0.0),
                "max_speed": c.get("speed", 0.0),
            })

        return {
            "name": "TEST",
            "scenario_name": "test",
            "players": len(external_cars),
            "roads": external_roads,
            "cars": external_cars
        }

    @staticmethod
    def deserialize(
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
        road_uid_to_horizontal = {}

        for r in ext_roads:
            road_uid = str(uuid.uuid4())
            road_name = r.get("name", "")
            road_name_to_uid[road_name] = road_uid

            horizontal = bool(r.get("horizontal"))
            road_uid_to_horizontal[road_uid] = horizontal

            # Reverse road position calculation: top = (position + offset) * 40
            road_offset = 12 if horizontal else 20
            position = (r.get("top", 0.0) / 40.0) - road_offset

            number_of_forward_lanes = r.get("right", 0)
            number_of_backward_lanes = r.get("left", 0)

            # Offset position because position of road is middle lane and not minimum x/y coordinate
            if horizontal:
                position += number_of_forward_lanes
            else:
                (number_of_forward_lanes, number_of_backward_lanes) = (number_of_backward_lanes, number_of_forward_lanes)
                position += number_of_backward_lanes

            internal_roads.append({
                "uid": road_uid,
                "name": road_name,
                "orientation": "HORIZONTAL" if horizontal else "VERTICAL",
                "position": position,
                "number_of_forward_lanes": number_of_forward_lanes,
                "number_of_backward_lanes": number_of_backward_lanes
            })

        internal_cars = []
        for idx, c in enumerate(ext_cars):
            start = c.get("start", {})
            road_name = start.get("road", "")
            direction = start.get("direction", "right")
            lane_val = start.get("lane", 0)
            road_uid = road_name_to_uid.get(road_name, "")

            # Reverse lane_index calculation
            if (direction in ["right", "down"] and road_uid_to_horizontal.get(road_uid)) or (direction in ["left", "up"] and not road_uid_to_horizontal.get(road_uid)):
                lane_index = lane_val
            else:
                lane_index = -(lane_val + 1)

            # Reverse car position calculation: position = (position_on_lane + offset) * 40
            horizontal = road_uid_to_horizontal.get(road_uid, False)
            car_offset = 20 if horizontal else 12
            ext_position = start.get("position", 0.0)
            position_on_lane = (ext_position / 40.0) - car_offset

            # Reverse color calculation: RGB tuple back to hex string
            ext_color = c.get("color", (173, 216, 230))
            if isinstance(ext_color, (list, tuple)) and len(ext_color) >= 3:
                color = "#{:02x}{:02x}{:02x}".format(int(ext_color[0]), int(ext_color[1]), int(ext_color[2]))
            else:
                color = str(ext_color)

            # Reverse length calculation: size = length * 40
            size = c.get("size", 40.0)
            length = size / 40.0

            internal_cars.append({
                "uid": str(uuid.uuid4()),
                "name": c.get("name", f"C{idx+1}"),
                "road_uid": road_uid,
                "lane_index": lane_index,
                "position_on_lane": position_on_lane,
                "transition": 0.0,
                "speed": c.get("speed", 0.0),
                "length": length,
                "color": color,
                "acceleration": 1.0,
                "next_turn": None
            })
            if c.get("max_speed", 0.0) > settings_model.max_speed:
                settings_model.max_speed = c.get("max_speed")

        TrafficSnapshotModel.from_dict(
            {"roads": internal_roads, "cars": internal_cars},
            traffic_snapshot_writer,
            traffic_snapshot_reader,
            settings_model
        )
