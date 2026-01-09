from dataclasses import dataclass

from PySide6.QtCore import Signal, QObject

@dataclass
class Settings(QObject):
    render_coordinate_system : bool
    render_safety_distance : bool
    breaking_acceleration: float

    change_breaking_acceleration = Signal()
    toggle_coordinate_system = Signal()
    toggle_safety_distance = Signal()

    def set_breaking_acceleration(self, breaking_acceleration: float):
        self.breaking_acceleration = breaking_acceleration
        self.change_breaking_acceleration.emit()

    def toggle_render_coordinate_system(self, render_coordinate_system: bool):
        self.render_coordinate_system = render_coordinate_system
        self.toggle_coordinate_system.emit()

    def toggle_render_safety_distance(self, render_safety_distance: bool):
        self.render_safety_distance = render_safety_distance
        self.toggle_safety_distance.emit()