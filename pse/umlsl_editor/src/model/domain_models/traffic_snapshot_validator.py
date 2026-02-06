from typing import TYPE_CHECKING

from pse.umlsl_editor.src.model.entities.road import RoadParams, RoadOrientation
from pse.umlsl_editor.src.model.errors.car_errors import CarTrafficSnapshotContextValidationError
from pse.umlsl_editor.src.model.errors.road_errors import RoadTrafficSnapshotContextValidationError
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent
from pse.umlsl_editor.src.view.view_constants import DIMENSION

if TYPE_CHECKING:
    from pse.umlsl_editor.src.model.entities.car import Car, CarParams
    from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel


class TrafficSnapshotValidator:
    """
    Handles validation logic for the TrafficSnapshotModel.
    Separated to keep the model clean and focused on state management.
    """

    def __init__(self, model: "TrafficSnapshotModel"):
        self._model = model

    def validate_car_params(self, car: "CarParams", new_instantiation: bool) -> None:
        """
        Validates a Car instance within the context of the TrafficSnapshot and throw errors if invalid.

        Args:
            car: The Car instance to validate.
            new_instantiation: Whether the car is being newly instantiated (True) or updated (False).

        Raises:
            CarTrafficSnapshotContextValidationError: If any validation check fails.
        """
        if new_instantiation:
            if not self._check_car_name_unique(car.name):
                raise CarTrafficSnapshotContextValidationError(
                    content=f"Car name '{car.name}' is not unique in the traffic snapshot.")
        if not self._check_lane_valid(car.lane):
            raise CarTrafficSnapshotContextValidationError(
                content=f"Car '{car.name}' has an invalid lane: {car.lane}.")
        if not self._check_transition_valid(car.transition, car.lane, car.speed < 0):
            raise CarTrafficSnapshotContextValidationError(
                content=f"Car '{car.name}' has an invalid transition: {car.transition} from lane {car.lane}.")

    def validate_car_and_autocorrect(self, car: "Car") -> bool:
        """
        Validates a Car instance within the context of the TrafficSnapshot and autocorrects if possible.

        Returns:
            True if the car is still valid, False if the car is no longer able to be in the traffic snapshot and should
            get removed.

        Args:
            car: The Car instance to validate.
        """
        if not self._check_lane_valid(car.lane):
            return False
        if not self._check_transition_valid(car.transition, car.lane, car.speed < 0):
            car.transition = 0.0
        if car.next_turn is not None and not self._check_turn_intent_valid(car.next_turn):
            car.next_turn = None
        return True

    def validate_road_params(self, road_params: RoadParams, new_instantiation: bool) -> None:
        """
        Validates a Road instance within the context of the TrafficSnapshot.

        Args:
            road_params: The Road instance to validate.
            new_instantiation: Whether the road is being newly instantiated (True) or updated (False).

        Raises:
            RoadTrafficSnapshotContextValidationError: If any validation check fails.
        """
        if new_instantiation:
            if not self._check_road_name_unique(road_params.name):
                raise RoadTrafficSnapshotContextValidationError(
                    content=f"Road name '{road_params.name}' is not unique in the traffic snapshot.")

        roads = self._model.get_roads().values()
        if road_params.orientation == RoadOrientation.HORIZONTAL:
            bounds: tuple[
                float, float] = road_params.position - road_params.number_of_forward_lanes * DIMENSION.LANE_WIDTH, road_params.position + road_params.number_of_backward_lanes * DIMENSION.LANE_WIDTH
        else:
            bounds: tuple[
                float, float] = road_params.position - road_params.number_of_backward_lanes * DIMENSION.LANE_WIDTH, road_params.position + road_params.number_of_forward_lanes * DIMENSION.LANE_WIDTH
        for road in roads:
            if road.name == road_params.name:
                continue
            if road.orientation == road_params.orientation:
                road_bounds = road.get_bounds()
                if max(bounds[0], road_bounds[0]) < min(bounds[1], road_bounds[1]):
                    print('errrorrrr')
                    raise RoadTrafficSnapshotContextValidationError(
                        content=f"Roads can't overlap each other. Please change position or number of forward or backward lanes.")

    def validate_road_and_autocorrect(self, road_uid: str) -> bool:
        """
        Validates a Road instance within the context of the TrafficSnapshot and autocorrects cars if necessary.

        Args:
            road_uid: The UID of the Road instance to validate.
        """
        raise NotImplementedError("Road validation and autocorrection is not implemented yet.")

    def _check_car_name_unique(self, car_name: str) -> bool:
        return car_name not in self._model.cars

    def _check_road_name_unique(self, road_name: str) -> bool:
        for road in self._model.roads.values():
            if road.name == road_name:
                return False
        return True

    def _check_uid_unique(self, uid: str) -> bool:
        for car in self._model.cars.values():
            if car.uid == uid:
                return False
        for road in self._model.roads.values():
            if road.uid == uid:
                return False
        return True

    def _check_lane_valid(self, lane: Lane) -> bool:
        """Check if the lane exists in the traffic snapshot."""
        road = self._model.get_road_by_uid(lane.road_uid)
        if lane in (road.forward_lanes + road.backward_lanes):
            return True
        return False

    def _check_transition_valid(self, transition: float, lane: Lane, car_driving_backwards: bool) -> bool:
        """Check if the transition value is valid for the given lane. It is not valid if the car changes out of the road,
        because right or left of the road is no lane. The transition value is aligned after the car
        (right is positive transition, left is negative) not the lane direction."""
        # TODO: Something wrong here
        if transition == 0.0:
            return True

        road = self._model.get_road_by_uid(lane.road_uid)
        new_lane_index = lane.lane_index + (1 if transition > 0 else -1) * (-1 if car_driving_backwards else 1)
        if new_lane_index > len(road.forward_lanes) - 1 or new_lane_index > -len(road.backward_lanes):
            return False
        return True

    def _check_turn_intent_valid(self, turn_intent: TurnIntent) -> bool:
        target_lane = turn_intent.target_lane
        return self._check_lane_valid(target_lane)
