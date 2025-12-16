from typing import Dict

from pse.umlsl_editor.src.core.car import Car
from pse.umlsl_editor.src.core.lane import Lane, LaneDirection
from pse.umlsl_editor.src.core.road import Road, RoadOrientation


class EntityFactory:
    """Creates all car and road objects to store in the traffic snapshot."""

    def __init__(self,):
        pass

    @staticmethod
    def create_car(self, name, assigned_road_id, lane_id, color, position_on_lane, transition, velocity,
                   length, next_turn) -> Car:
        """Creates a car object."""

        return Car(name, assigned_road_id, lane_id, color, position_on_lane, transition, velocity,
                   length, next_turn)

    @staticmethod
    def create_road(self, name: str, orientation: RoadOrientation,
                    position: float, lanes: Dict[str, Lane]) -> Road:
        """Creates a road object."""

        return Road(name, orientation, position, lanes)

    @staticmethod
    def create_lane(self, index: int, direction: LaneDirection) -> Lane:
        """Creates a lane object."""

        return Lane(index, direction)