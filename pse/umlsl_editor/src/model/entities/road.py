from dataclasses import dataclass
from enum import Enum

from pse.umlsl_editor.src.model.entities.entity import Entity
from pse.umlsl_editor.src.model.errors.road_errors import RoadValidationError
from pse.umlsl_editor.src.model.helper.uid_service import generate_uid


class RoadOrientation(Enum):
    """
    Enumeration representing the orientation of a road in the coordinate system.

    Attributes:
        HORIZONTAL: The road runs horizontally (left-right) in the coordinate system.
        VERTICAL: The road runs vertically (up-down) in the coordinate system.
    """

    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


class LaneDirection(Enum):
    """
    Enumeration representing the direction of traffic flow in a lane.

    Attributes:
        FORWARD: Traffic flows in the forward direction (represented as 'fn').
        BACKWARD: Traffic flows in the backward direction (represented as 'bn').
    """

    FORWARD = "fn"
    BACKWARD = "bn"



@dataclass
class RoadParams:
    """
    Type-safe parameter dictionary for Road creation.

    Supports all Road attributes with optional parameters marked appropriately.
    Use this with **kwargs to avoid repetitive parameter forwarding.

    Attributes:
        name: Unique human-readable identifier for the road.
        orientation: The orientation of the road (horizontal or vertical).
        position: The position of the road in the coordinate system.
        forward_lanes: Number of lanes in the forward direction
        backward_lanes: Number of lanes in the backward direction
    """
    name: str
    orientation: RoadOrientation
    position: float
    forward_lanes: int
    backward_lanes: int


@dataclass
class Road(Entity):
    """
    Represents a road in the traffic simulation system.

    A road is an infinite linear line with a specific orientation (horizontal or vertical)
    and contains one or more lanes in either forward or backward direction.
    Roads only define the number of forward and backward lanes.

    Attributes:
        name: Unique human-readable identifier for the road.
              Must be a non-empty string.
        orientation: The orientation of the road (HORIZONTAL or VERTICAL).
        position: The position of the road in the coordinate system along the
                  axis perpendicular to its orientation. For horizontal roads,
                  this is the Y-coordinate; for vertical roads, the X-coordinate.
        forward_lanes: Number of lanes in the forward direction
        backward_lanes: Number of lanes in the backward direction

    Raises:
        RoadValidationError: If name is empty, orientation is invalid,
                             or position is not a valid number.
    """

    name: str
    orientation: RoadOrientation
    position: float
    forward_lanes: int
    backward_lanes: int

    _should_validate: bool = False

    @classmethod
    def from_params(cls, params: RoadParams) -> "Road":
        """
        Creates a Road instance from a RoadParams object.

        Args:
            params: An instance of RoadParams containing the road attributes.
        Returns:
            A new Road instance with the provided parameters.
        """
        return cls(
            name=params.name,
            uid=generate_uid(),
            orientation=params.orientation,
            position=params.position,
            forward_lanes=params.forward_lanes,
            backward_lanes=params.backward_lanes,
        )

    def update_from_params(self, params: RoadParams) -> None:
        """
        Updates the Road instance's attributes based on a RoadParams object.

        Args:
            params: An instance of RoadParams containing the new road attributes.

        Raises:
            RoadValidationError: If any validation check fails.
        """
        self._should_validate = False
        self.name = params.name
        self.orientation = params.orientation
        self.position = params.position
        self.forward_lanes = params.forward_lanes
        self.backward_lanes = params.backward_lanes
        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Validates the Road instance after initialization.

        Raises:
            RoadValidationError: If any validation check fails.
        """
        self.validate()
        self._initialized = True
        self._should_validate = True

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        if getattr(self, "_initialized", False) and getattr(self, "_should_validate", True):
            self.validate()

    def validate(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise RoadValidationError(content="Name must be a non-empty string.")

        if not isinstance(self.orientation, RoadOrientation):
            raise RoadValidationError(content="Orientation must be a RoadOrientation enum member.")

        if not isinstance(self.position, (int, float)):
            raise RoadValidationError(content="Position must be a number.")

        if not isinstance(self.forward_lanes, int) or self.forward_lanes < 0:
            raise RoadValidationError(content="Forward lanes must be a non-negative integer.")

        if not isinstance(self.backward_lanes, int) or self.backward_lanes < 0:
            raise RoadValidationError(content="Backward lanes must be a non-negative integer.")

        if self.forward_lanes == 0 and self.backward_lanes == 0:
            raise RoadValidationError(content="Road must have at least one lane.")
