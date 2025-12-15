from typing import Optional


class SelectionContext:
    """Handles logic for selecting entities (DC10)."""

    def __init__(self):
        self.selected_entity_id: Optional[str] = None
        self.selected_type: Optional[str] = None  # 'car' or 'road'

    def select(self, id_: str, type_: str):
        pass

    def deselect(self):
        pass
