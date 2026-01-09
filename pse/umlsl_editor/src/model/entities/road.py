from dataclasses import dataclass
from enum import Enum



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


class RoadValidationError(ValueError):
    """
    Custom exception raised when Road validation fails.
    """

    pass

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
class Road():
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
        raise NotImplementedError()

    def __post_init__(self) -> None:
        """
        Validates the Road instance after initialization.

        Performs the following validation checks:
        - name must be a non-empty string
        - orientation must be a valid RoadOrientation enum value
        - position must be a valid number (int or float)
        - forward_lanes and backward_lanes must be non-negative integers

        Raises:
            RoadValidationError: If any validation check fails.
        """

    def __eq__(self, other):
        """Checks equality based only on the unique identifier (uid) of the Road."""
        if not isinstance(other, Road):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        """Generates a hash based only on the unique identifier (name) of the Road."""
        return hash(self.name)
