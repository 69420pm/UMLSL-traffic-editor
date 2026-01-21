from dataclasses import dataclass

from pse.umlsl_editor.src.model.helper.observables import Observable
from pse.umlsl_editor.src.model.helper.event_types import SettingsEventType

@dataclass
class SettingsModel(Observable):
    """
    Application settings model using Observable pattern.

    Events:
        - SettingsEventType.CHANGE_BREAKING_ACCELERATION: Fired when breaking acceleration changes (data: float)
        - SettingsEventType.TOGGLE_COORDINATE_SYSTEM: Fired when coordinate system is toggled (data: bool)
        - SettingsEventType.TOGGLE_SAFETY_DISTANCE: Fired when safety distance is toggled (data: bool)
    """
    render_coordinate_system : bool
    render_safety_distance : bool
    breaking_acceleration: float

    def __post_init__(self):
        """Initialize Observable after dataclass initialization."""
        Observable.__init__(self)

    def set_breaking_acceleration(self, breaking_acceleration: float):
        self.breaking_acceleration = breaking_acceleration
        self.notify(SettingsEventType.CHANGE_BREAKING_ACCELERATION, breaking_acceleration)

    def toggle_render_coordinate_system(self, render_coordinate_system: bool):
        self.render_coordinate_system = render_coordinate_system
        self.notify(SettingsEventType.TOGGLE_COORDINATE_SYSTEM, render_coordinate_system)

    def toggle_render_safety_distance(self, render_safety_distance: bool):
        self.render_safety_distance = render_safety_distance
        self.notify(SettingsEventType.TOGGLE_SAFETY_DISTANCE, render_safety_distance)
