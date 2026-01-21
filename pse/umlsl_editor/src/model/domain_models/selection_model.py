from dataclasses import dataclass

from pse.umlsl_editor.src.model.entities.entity import Entity
from pse.umlsl_editor.src.model.helper.event_types import SelectionEventType
from pse.umlsl_editor.src.model.helper.observables import Observable


@dataclass
class SelectionModel(Observable):
    """Selection model using Observable pattern."""

    selected_entity: Entity | None = None
    """ The currently selected entity, or None if no entity is selected. 
    At any point of time there is at most one selected entity."""

    def __post_init__(self):
        """Initialize Observable after dataclass initialization."""
        Observable.__init__(self)

    def select_entity(self, entity: Entity):
        """Selects the given entity."""
        self.selected_entity = entity
        self.notify(SelectionEventType.ENTITY_SELECTED, entity)

    def unselect_entity(self, entity: Entity):
        """Unselects the given entity if it is currently selected. Does nothing otherwise."""
        if self.selected_entity == entity:
            self.selected_entity = None
            self.notify(SelectionEventType.ENTITY_DESELECTED, entity)

    def clear_selection(self):
        """Clears the current selection."""
        self.selected_entity = None
        self.notify(SelectionEventType.SELECTION_CLEARED)
