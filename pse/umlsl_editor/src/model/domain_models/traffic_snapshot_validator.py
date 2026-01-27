from typing import TYPE_CHECKING, Optional

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.entities.road import Road, LaneDirection
from pse.umlsl_editor.src.model.errors.car_errors import CarTrafficSnapshotContextValidationError
from pse.umlsl_editor.src.model.errors.road_errors import RoadTrafficSnapshotContextValidationError
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent

if TYPE_CHECKING:
    from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel


class TrafficSnapshotValidator:
    """
    Handles validation logic for the TrafficSnapshotModel.
    Separated to keep the model clean and focused on state management.
    """

    def __init__(self, model: "TrafficSnapshotModel"):
        self._model = model

    def validate_car(self, car: Car, new_instantiation: bool) -> None:
        """
        Validates a Car instance within the context of the TrafficSnapshot and throw errors if invalid.

        Args:
            car: The Car instance to validate.
            new_instantiation: Whether the car is being newly instantiated (True) or updated (False).

        Raises:
            CarTrafficSnapshotContextValidationError: If any validation check fails.
        """
        if new_instantiation:
            if not self._check_uid_unique(car.uid):
                raise CarTrafficSnapshotContextValidationError(
                    content=f"Car UID '{car.uid}' is not unique in the traffic snapshot.")
            if not self._check_car_name_unique(car.name):
                raise CarTrafficSnapshotContextValidationError(
                    content=f"Car name '{car.name}' is not unique in the traffic snapshot.")
        if not self._check_lane_valid(car.lane):
            raise CarTrafficSnapshotContextValidationError(
                content=f"Car '{car.name}' has an invalid lane: {car.lane}.")
        if not self._check_transition_valid(car.transition, car.lane, car.velocity < 0):
            raise CarTrafficSnapshotContextValidationError(
                content=f"Car '{car.name}' has an invalid transition: {car.transition} from lane {car.lane}.")

    def validate_car_and_autocorrect(self, car: Car) -> bool:
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
        if not self._check_transition_valid(car.transition, car.lane, car.velocity < 0):
            car.transition = 0.0
        if car.next_turn is not None and not self._check_turn_intent_valid(car.next_turn):
            car.next_turn = None
        return True

    def validate_road(self, road: Road, new_instantiation: bool) -> None:
        """
        Validates a Road instance within the context of the TrafficSnapshot.

        Args:
            road: The Road instance to validate.
            new_instantiation: Whether the road is being newly instantiated (True) or updated (False).

        Raises:
            RoadTrafficSnapshotContextValidationError: If any validation check fails.
        """
        if new_instantiation:
            if not self._check_uid_unique(road.uid):
                raise RoadTrafficSnapshotContextValidationError(
                    content=f"Road UID '{road.uid}' is not unique in the traffic snapshot.")
            if not self._check_road_name_unique(road.name):
                raise RoadTrafficSnapshotContextValidationError(
                    content=f"Road name '{road.name}' is not unique in the traffic snapshot.")

    def _check_car_name_unique(self, car_name: str) -> bool:
        return car_name not in self._model.cars

    def _check_road_name_unique(self, road_name: str) -> bool:
        return road_name not in self._model.roads

    def _check_uid_unique(self, uid: str) -> bool:
        for car in self._model.cars.values():
            if car.uid == uid:
                return False
        for road in self._model.roads.values():
            if road.uid == uid:
                return False
        return True

    def _check_lane_valid(self, lane: Lane) -> bool:
        if lane.road_uid not in self._model._roads:
            return False

        road = self._model._roads[lane.road_uid]

        if lane.lane_direction is LaneDirection.FORWARD:
            if lane.lane_index > road.forward_lanes:
                return False
        elif lane.lane_direction is LaneDirection.BACKWARD:
            if lane.lane_index > road.backward_lanes:
                return False
        else:
            return False
        return True

    def _check_transition_valid(self, transition: float, lane: Lane, car_driving_backwards: bool) -> bool:
        """Check if the transition value is valid for the given lane. It is not valid if the car changes out of the road,
        because right or left of the road is no lane. The transition value is aligned after the car
        (right is positive transition, left is negative) not the lane direction."""

        road = self._model._roads.get(lane.road_uid)
        if road is None:
            return False

        lane_index_to_check = lane.lane_index + (1 if transition > 0 else -1) * (
            -1 if car_driving_backwards else 1)

        if lane.lane_direction is LaneDirection.FORWARD:
            if lane_index_to_check > road.forward_lanes or (
                    (lane_index_to_check <= 0) and road.backward_lanes >= 1):
                return False
        elif lane.lane_direction is LaneDirection.BACKWARD:
            if lane_index_to_check > road.backward_lanes or (
                    (lane_index_to_check <= 0) and road.forward_lanes >= 1):
                return False
        return True

    def _check_turn_intent_valid(self, turn_intent: TurnIntent) -> bool:
        target_lane = turn_intent.target_lane
        return self._check_lane_valid(target_lane)
