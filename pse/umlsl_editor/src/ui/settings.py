from dataclasses import dataclass, field


@dataclass
class Settings:
    """Global settings (MC7, MC5)."""

    braking_acceleration: float = field(default=4.5)
    """Braking acceleration in units/s². The larger the shorter the breaking distance"""
    show_safety_spaces: bool = field(default=True)
    """Whether to show safety spaces around cars."""
    show_grid: bool = field(default=False)
    """Whether to show grid lines on the canvas."""
