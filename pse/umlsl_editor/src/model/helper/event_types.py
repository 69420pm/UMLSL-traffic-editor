"""Event type enums for the observer pattern implementation."""
from enum import Enum, auto


class TrafficSnapshotEventType(Enum):
    """Event types emitted by TrafficSnapshot."""
    CAR_ADDED = auto()
    CAR_REMOVED = auto()
    CAR_UPDATED = auto()
    ROAD_ADDED = auto()
    ROAD_REMOVED = auto()
    ROAD_UPDATED = auto()
    CROSSING_SEGMENT_ADDED = auto()
    CROSSING_SEGMENT_REMOVED = auto()
    CROSSING_SEGMENT_UPDATED = auto()
    TRAFFIC_SNAPSHOT_WARNING = auto()

    SEGMENTS_RECALCULATED = auto()


class SettingsEventType(Enum):
    """Event types emitted by Settings."""
    CHANGE_BREAKING_ACCELERATION = auto()
    TOGGLE_COORDINATE_SYSTEM = auto()
    TOGGLE_SAFETY_DISTANCE = auto()


class UMLSLQueriesEventType(Enum):
    """Event types emitted by UMLSLQueries."""
    UMLSL_QUERY_ADDED = auto()
    UMLSL_QUERY_REMOVED = auto()
    UMLSL_QUERY_UPDATED = auto()
    UMLSL_QUERY_WARNING = auto()

class SelectionEventType(Enum):
    """Event types emitted by SelectionModel."""
    ENTITY_SELECTED = auto()
    ENTITY_DESELECTED = auto()
    SELECTION_CLEARED = auto()