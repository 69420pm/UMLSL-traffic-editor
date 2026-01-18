"""
View constants for the UMLSL Traffic Editor.

This module contains all visual constants used throughout the view layer,
organized into logical groups for Z-ordering, dimensions, colors, and UI paths.
"""
from dataclasses import dataclass, field
from PySide6.QtGui import QColor


@dataclass(frozen=True)
class _ZLayers:
    """Controls the drawing order (Z-Index) for scene items."""
    ROAD: int = 0
    CROSSING: int = 1
    CAR: int = 10
    OVERLAY: int = 100


@dataclass(frozen=True)
class _Dimension:
    """Physical dimensions and rendering scales."""
    # Lane and car dimensions (in scene units)
    LANE_WIDTH: float = 1.0
    CAR_WIDTH: float = 0.8

    # Scene configuration
    SCENE_SIZE: int = 1000

    # Zoom constraints
    MAX_ZOOM: float = 100.0
    MIN_ZOOM: float = 3.0
    INITIAL_ZOOM: float = 20.0
    BUTTON_ZOOM_AMOUNT: float = 1.4

    # Zoom thresholds for detail levels
    LANE_LABEL_MIN_ZOOM: float = 20.0
    GRID_FINE_THRESHOLD: float = 20.0

    # Grid spacing
    GRID_STEP_COARSE: float = 10.0
    GRID_STEP_FINE: float = 1.0

    # Line widths
    LINE_WIDTH_ROAD_DIVIDER: float = 0.1

    # Zoom sensitivity
    TOUCHPAD_ZOOM_SENSITIVITY: float = 0.01
    WHEEL_ZOOM_SENSITIVITY: float = 0.001

    # Label drawing
    LABEL_PADDING: int = 5


@dataclass(frozen=True)
class _Colors:
    """Standard UI colors for the traffic editor."""
    # Background colors
    BACKGROUND: QColor = field(default_factory=lambda: QColor("#011C26"))
    LAYER: QColor = field(default_factory=lambda: QColor("#032F40"))

    # Text and UI elements
    TEXT: QColor = field(default_factory=lambda: QColor("#F9F9F9"))

    # Status colors
    GREEN: QColor = field(default_factory=lambda: QColor("#799582"))
    RED: QColor = field(default_factory=lambda: QColor("#D97855"))

    # Utility
    TRANSPARENT: QColor = field(default_factory=lambda: QColor(0, 0, 0, 0))

@dataclass(frozen=True)
class _UIPaths:
    """Paths to UI resource files (relative to the widgets folder)."""
    MAIN_WINDOW: str = "../widgets/main.ui"
    LIST_ITEM: str = "ui/list.ui"
    CAR_EDIT: str = "../widgets/car_edit.ui"


# --- Public Singleton Instances ---
Z_LAYERS = _ZLayers()
DIMENSION = _Dimension()
COLORS = _Colors()
UI_PATHS = _UIPaths()
