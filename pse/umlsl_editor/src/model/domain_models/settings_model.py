from dataclasses import dataclass

from pse.umlsl_editor.src.model.helper.event_types import SettingsEventType
from pse.umlsl_editor.src.model.helper.observables import Observable


@dataclass
class SettingsModel(Observable):
    """
    """

    braking_acceleration: float
    max_speed: float

    def __post_init__(self):
        """Initialize Observable after dataclass initialization."""
        Observable.__init__(self)

    def set_braking_acceleration(self, braking_acceleration: float):
        self.braking_acceleration = braking_acceleration
        self.notify(SettingsEventType.CHANGE_BREAKING_DECELERATION, braking_acceleration)

    def set_max_speed(self, max_acceleration: float):
        self.max_speed = max_acceleration
        self.notify(SettingsEventType.CHANGE_MAX_ACCELERATION, max_acceleration)

    def braking_distance(self) -> float:
        return self.max_speed * self.max_speed / (2.0 * self.braking_acceleration)
