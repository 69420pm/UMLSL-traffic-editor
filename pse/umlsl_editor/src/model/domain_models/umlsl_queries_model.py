from dataclasses import dataclass
from typing import Any

from pse.umlsl_editor.src.commands.umlsl import add_umlsl_query
from pse.umlsl_editor.src.model.helper.observables import Observable, ObservableList, ObservableDict
from pse.umlsl_editor.src.model.helper.event_types import UMLSLQueriesEventType
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery

class UMLSLQueriesValidationError(Exception):
    """Raised when UMLSL queries validation fails in the context of a traffic snapshot."""
    pass

@dataclass
class UMLSLQueriesModel(Observable):
    """
    UMLSL queries model using Observable pattern.

    Events:
        - UMLSLQueriesEventType.UMLSL_QUERY_ADDED: Fired when a query is added (data: UMLSLQuery)
        - UMLSLQueriesEventType.UMLSL_QUERY_REMOVED: Fired when a query is removed (data: UMLSLQuery)
        - UMLSLQueriesEventType.UMLSL_QUERY_UPDATED: Fired when a query is updated (data: UMLSLQuery)
    """
    def __init__(self, queries: dict[str, UMLSLQuery]=None) -> None:
        self._queries = ObservableDict(
            on_add=lambda query: self.notify(UMLSLQueriesEventType.UMLSL_QUERY_ADDED, query),
            on_remove=lambda query: self.notify(UMLSLQueriesEventType.UMLSL_QUERY_REMOVED, query),
            on_update=lambda query: self.notify(UMLSLQueriesEventType.UMLSL_QUERY_UPDATED, query),
            initial_data=queries)
        super().__init__()

    def __post_init__(self):
        """Initialize Observable after dataclass initialization."""
        Observable.__init__(self)

    def add_umlsl_query(self, umlsl_query: UMLSLQuery) -> None:
        """
        Adds a UMLSL query to the snapshot and validates all attributes in the context of the snapshot.
        Raises:
            TrafficSnapshotValidationError: If the UMLSL query is invalid in the context of the snapshot.
        """
        self._queries[umlsl_query.uid] = umlsl_query

    def remove_umlsl_query(self, query_id: str) -> None:
        """
        Removes a UMLSL query from the snapshot.
        """
        self._queries.pop(query_id)

    def update_umlsl_query(self, umlsl_query_data: UMLSLQuery) -> None:
        """
        Updates an existing UMLSL query in the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            UMLSLQueriesValidationError: If the updated UMLSL query is invalid in the context of the snapshot.
        """
        self._queries[umlsl_query_data.uid] = umlsl_query_data

    def to_dict(self) -> dict[str, Any]:
        """
        Serializes the UMLSL_queries instance to a dictionary suitable for JSON encoding.
        """
        return self._queries.__dict__()

    def to_json(self) -> str:
        """
        Serializes the UMLSL_queries instance to a JSON string.
        """
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UMLSLQuery":
        """
        Creates a UMLSL_queries instance from a dictionary.

        Args:
            data: A dictionary containing the queries.
        """
        raise NotImplementedError

    @classmethod
    def from_json(cls, json_string: str) -> "UMLSLQuery":
        """
        Creates a UMLSLQuery instance from a JSON string.

        Args:
            json_string: A JSON-formatted string containing umlsl query data.

        """
        raise NotImplementedError