"""
Road accessor protocol for the UMLSL Traffic Editor.

Defines the interface for accessing road data needed by view models.
"""
from typing import Protocol, Optional

from pse.umlsl_editor.src.model.entities.road import Road


class RoadAccessor(Protocol):
    """Protocol for objects that can provide road data by name."""

    def get_road(self, road_name: str) -> Optional[Road]:
        """
        Retrieve a road by its name.

        Args:
            road_name: The unique name of the road.

        Returns:
            The Road object if found, otherwise None.
        """
        ...