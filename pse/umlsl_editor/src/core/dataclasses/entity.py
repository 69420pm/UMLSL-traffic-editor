from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Entity(ABC):
    """
    Abstract base class for all entities in the traffic simulation.

    Attributes:
        name: Unique human-readable identifier for the entity. Must be a non-empty string.
    """

    name: str

    @abstractmethod
    def __post_init__(self) -> None:
        """
        Validates the Entity attributes after initialization.

        Must be implemented by subclasses to perform validation checks.

        Raises:
            ValueError: If any validation check fails.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the Entity instance to a dictionary suitable for JSON encoding.

        Returns:
            A dictionary representation of the entity.
        """
        pass

    def to_json(self) -> str:
        """
        Serializes the Entity instance to a JSON string.

        Returns:
            A JSON-formatted string representation of the entity.
        """
        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict[str, Any]) -> "Entity":
        """
        Creates an Entity instance from a dictionary.

        Args:
            data: A dictionary containing entity data.

        Returns:
            A new Entity instance populated with the provided data.
        """
        pass

    @classmethod
    def from_json(cls, json_string: str) -> "Entity":
        """
        Creates an Entity instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing entity data.

        Returns:
            A new Entity instance populated with the parsed JSON data.
        """
        raise NotImplementedError()

    def __repr__(self) -> str:
        """
        Returns a detailed string representation of the Entity.
        """
        raise NotImplementedError()

