import re
from dataclasses import dataclass
from typing import Optional

from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.entity import Entity
from pse.umlsl_editor.src.model.errors.car_errors import CarValidationError
from pse.umlsl_editor.src.model.helper.uid_service import generate_uid
from pse.umlsl_editor.src.model.traffic_value_objects.lane import Lane
from pse.umlsl_editor.src.model.traffic_value_objects.segments.car_environment import CarEnvironment
from pse.umlsl_editor.src.model.traffic_value_objects.turn_intent import TurnIntent


@dataclass
class CarParams:
    """
    Type-safe parameter dictionary for Car creation.

    Supports all Car attributes with optional parameters marked appropriately.
    Use this with **kwargs to avoid repetitive parameter forwarding.

    Attributes:
        name: Unique human-readable identifier for the car.
        lane: Lane the car is currently in, defined by road, lane index, and direction.
        color: Hex color code for rendering.
        position_on_lane: Distance along the lane in units
        transition: Lane change progress from -1.0 to 1.0 exclusive
        speed: Current speed of the car in units per time step
        length: Physical length of the car in units
        next_turn: Optional intended turn behavior at the next intersection
    """
    name: str
    lane: Lane | None
    color: str
    position_on_lane: float
    transition: float
    speed: float
    length: float
    next_turn: TurnIntent | None
    acceleration: float
    braking_distance: float


@dataclass()
class Car(Entity):
    """
    Represents a car/vehicle in the traffic simulation.

    A car is a movable entity that travels along lanes on roads. It has physical
    properties (length, color), kinematic properties (position, velocity), and
    navigational properties (assigned road, lane, transition state, next turn).

    Attributes:
        name: Unique human-readable identifier for the car. Must be a non-empty string.
        lane: Lane the car is currently in, defined by road, lane index, and direction.
        color: Hex color code for rendering the car.
        position_on_lane: Distance along the lane in units. Must be non-negative.
        transition: Lane change progress from -1.0 (fully left) to 1.0 (fully right).
                    Value of 0.0 means centered in current lane. Bounds are exclusive.
        speed: Current speed of the car in units per time step. Can be negative for reverse.
        length: Physical length of the car in units. Must be positive.
        next_turn: Optional intended turn behavior at the next intersection.

        reserved_lanes: List of LaneSegments reserved by the car for future movement.
        claimed_lanes: List of LaneSegments currently claimed by the car.
        reserved_crossings: List of CrossingSegments reserved by the car.
        claimed_crossings: List of CrossingSegments currently claimed by the car.
        path: Path is list of LaneSegments and CrossingSegments representing the planned route.
        acceleration: Current acceleration of the car in units per time step squared.

    Raises:
        CarValidationError: If any validation check fails during instantiation.
    """
    name: str

    lane: Lane

    color: str

    position_on_lane: float

    transition: float

    speed: float

    length: float

    next_turn: Optional[TurnIntent]

    # class: Path
    # Descriptions: all segments that lay in view of car, only single lane
    # segments: list[Segment]

    # class LaneInterval:
    # segment: LaneSegment
    # start: float
    # end: float

    # class LaneSegment:
    # on_lane: Lane
    # start_road: str
    # end_road: str

    # class CrossingSegment:
    # laneA: Lane
    # laneB: Lane

    environment: CarEnvironment
    acceleration: float

    _should_validate: bool = False

    @classmethod
    def from_params(cls, params: CarParams, traffic_snapshot: TrafficSnapshotReader) -> "Car":
        """
        Creates a Car instance from a CarParams dataclass.

        Args:
            params: CarParams instance containing all car attributes.

        Returns:
            A new Car instance with attributes from the params.
        """

        """"
        if params.next_turn is None:
            car_env = CarEnvironment.empty()
        else:
            car_env = CarEnvironment.create_environment(
                ts_reader,
                params.lane,
                params.position_on_lane,
                params.length,
                params.speed,
                params.next_turn
            )
        """

        car_env = CarEnvironment.create_environment(
            traffic_snapshot,
            params.lane,
            params.position_on_lane,
            params.length,
            params.speed,
            params.next_turn,
            params.braking_distance
        )
        return cls(
            uid=generate_uid(),
            name=params.name,
            lane=params.lane,
            color=params.color,
            position_on_lane=params.position_on_lane,
            transition=params.transition,
            speed=params.speed,
            length=params.length,
            next_turn=params.next_turn,
            environment=car_env,
            acceleration=params.acceleration,
        )

    def __post_init__(self) -> None:
        """
        Validates the Car attributes after initialization without checking them in the TrafficSnapshot context.

        Raises:
            CarValidationError: If any validation check fails.
        """
        self.validate()
        self._should_validate = True

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        if getattr(self, "_initialized", False) and getattr(self, "_should_validate", True):
            self.validate()

    def validate(self) -> None:
        if not isinstance(self.name, str):
            raise CarValidationError(content="Name must be a non-empty string.")

        if self.name.strip() == "":
            raise CarValidationError(content="Name cannot be empty.")

        if not isinstance(self.lane, Lane):
            raise CarValidationError(content="Lane must be a Lane instance.")

        if not isinstance(self.color, str) or not re.match(r'^#(?:[0-9a-fA-F]{3}){1,2}$', self.color):
            """
            No need for color checking. Color can be hex or a color name like red, blue, green, etc.
            If string doesnt match hex code or color name, it will result in black.
            If you want to enforce hex color codes only, uncomment the following line.
            """
            # raise CarValidationError(content="Color must be a valid hex color code.")
            pass

        # Transition bounds check (-1.0, 1.0) exclusive
        if not (-1.0 < self.transition < 1.0):
            raise CarValidationError(content="Transition must be in the range (-1.0, 1.0) exclusive.")

        if not isinstance(self.speed, (int, float)):
            raise CarValidationError(content="Velocity must be a number.")

        if self.length <= 0:
            raise CarValidationError(content="Length must be a positive number.")

        if self.next_turn is not None and not isinstance(self.next_turn, TurnIntent):
            raise CarValidationError(content="Next turn must be None or a TurnIntent instance.")

    def update_from_params(self, params: CarParams, traffic_snapshot: TrafficSnapshotReader) -> None:
        """
        Updates the Car instance's attributes based on a CarParams dataclass.

        Args:
            params: CarParams instance containing updated car attributes.

        Raises:
            CarValidationError: If any validation check fails.
        """

        """"
        
        if params.next_turn is None:
            car_env = CarEnvironment.empty()
        else:
            car_env = CarEnvironment.create_environment(
                ts_reader,
                params.lane,
                params.position_on_lane,
                params.length,
                params.speed,
                params.next_turn
            )

        """

        car_env = CarEnvironment.create_environment(
            traffic_snapshot,
            params.lane,
            params.position_on_lane,
            params.length,
            params.speed,
            params.next_turn,
            params.braking_distance
        )

        self.environment = car_env

        self._should_validate = False
        self.name = params.name
        self.lane = params.lane
        self.color = params.color
        self.position_on_lane = params.position_on_lane
        self.transition = params.transition
        self.speed = params.speed
        self.length = params.length
        self.next_turn = params.next_turn
        self.acceleration = params.acceleration
        self.__post_init__()

    def absolute_position(self) -> float:
        raise NotImplementedError
        # return self.lane.road_name.position + self.position_on_lane
