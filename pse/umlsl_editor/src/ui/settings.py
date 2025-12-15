class SimulationSettings:
    """Global settings (MC7, MC5)."""
    def __init__(self):
        self.braking_acceleration: float = 5.0
        self.show_safety_spaces: bool = False
        self.show_grid: bool = True