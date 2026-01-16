from typing import Protocol, Optional
from pse.umlsl_editor.src.model.entities.road import Road

class RoadAccessor(Protocol):
    def get_road(self, road_name: str) -> Optional[Road]:
        """Returns a Road object if found, else None."""
        ...