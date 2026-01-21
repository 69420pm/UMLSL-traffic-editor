from abc import ABC
from dataclasses import dataclass


@dataclass
class Entity(ABC):
    """Abstract base class for all entities in the UMLSL editor."""
    uid: str