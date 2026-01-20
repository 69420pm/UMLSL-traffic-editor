from abc import ABC
from dataclasses import dataclass


@dataclass
class Entity(ABC):
    uid: str