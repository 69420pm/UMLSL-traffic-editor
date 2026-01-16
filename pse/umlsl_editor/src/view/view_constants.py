# pse/umlsl_editor/src/view/view_constants.py
from dataclasses import dataclass, field
from PySide6.QtGui import QColor


@dataclass(frozen=True)
class _ZLayers:
    """Controls the drawing order (Z-Index)."""
    ROAD: int = 0
    CROSSING: int = 1
    CAR: int = 10
    OVERLAY: int = 100


@dataclass(frozen=True)
class _Dimension:
    """Physical dimensions and rendering scales."""
    LANE_WIDTH: float = 40.0
    CAR_WIDTH: float = 30.0
    SCENE_SIZE: int = 100*LANE_WIDTH


@dataclass(frozen=True)
class _Colors:
    """Standard UI colors."""
    BACKGROUND: QColor = field(default_factory=lambda: QColor("#011C26"))
    LAYER: QColor = field(default_factory=lambda: QColor("#032F40"))
    TEXT: QColor = field(default_factory=lambda: QColor("#F9F9F9"))
    GREEN: QColor = field(default_factory=lambda: QColor("#799582"))
    RED: QColor = field(default_factory=lambda: QColor("#D97855"))



# Public accessors (singleton-like usage)
Z_LAYERS = _ZLayers()
DIMENSION = _Dimension()
COLORS = _Colors()