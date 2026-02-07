from dataclasses import dataclass

from pse.umlsl_editor.src.model.helper.event_types import SettingsEventType
from pse.umlsl_editor.src.model.helper.observables import Observable


@dataclass
class SettingsModel(Observable):
    """
    """

    breaking_deceleration: float
    max_acceleration: float

    def __post_init__(self):
        """Initialize Observable after dataclass initialization."""
        Observable.__init__(self)

    def set_breaking_deceleration(self, breaking_deceleration: float):
        self.breaking_deceleration = breaking_deceleration
        self.notify(SettingsEventType.CHANGE_BREAKING_DECELERATION, breaking_deceleration)

    def set_max_acceleration(self, max_acceleration: float):
        self.max_acceleration = max_acceleration
        self.notify(SettingsEventType.CHANGE_MAX_ACCELERATION, max_acceleration)

    def braking_distance(self) -> float:
        return self.max_acceleration * self.max_acceleration / (2.0 * self.breaking_deceleration)
