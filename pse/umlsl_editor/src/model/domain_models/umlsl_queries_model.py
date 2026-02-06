from dataclasses import dataclass
from typing import Any

from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery, UMLSLQueryParams
from pse.umlsl_editor.src.model.errors.umlsl_query_errors import UMLSLQueryValidationError
from pse.umlsl_editor.src.model.helper.event_types import UMLSLQueriesEventType
from pse.umlsl_editor.src.model.helper.observables import Observable, ObservableDict


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

    def __init__(self, queries: dict[str, UMLSLQuery] = None) -> None:
        self._queries = ObservableDict(
            on_add=lambda query: self.notify(UMLSLQueriesEventType.UMLSL_QUERY_ADDED, query),
            on_remove=lambda query: self.notify(UMLSLQueriesEventType.UMLSL_QUERY_REMOVED, query),
            on_update=lambda query: self.notify(UMLSLQueriesEventType.UMLSL_QUERY_UPDATED, query),
            initial_data=queries)
        super().__init__()

    def __post_init__(self):
        """Initialize Observable after dataclass initialization."""
        Observable.__init__(self)

    def get_query_by_id(self, uid: str) -> UMLSLQuery:
        if uid not in self._queries:
            raise UMLSLQueryValidationError(f"UMLSL Query with UID {uid} does not exist.")
        return self._queries[uid]

    def get_queries(self) -> dict[str, UMLSLQuery]:
        """Return all UMLSL queries as a plain dictionary."""
        return dict(self._queries.__dict__())

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

    def update_umlsl_query(self, umlsl_query_data: UMLSLQuery, query_params: UMLSLQueryParams) -> None:
        """
        Updates an existing UMLSL query in the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            UMLSLQueriesValidationError: If the updated UMLSL query is invalid in the context of the snapshot.
        """
        umlsl_query_data.update_from_params(query_params)
        self._queries[umlsl_query_data.uid] = umlsl_query_data

    def to_dict(self) -> list[dict[str, Any]]:
        """
        Serializes the UMLSL_queries instance to a list of dictionaries suitable for JSON encoding.
        """
        return [
            {
                "uid": query.uid,
                "latex": query.latex,
                "assigned_car_uid": query.assigned_car_uid,
            }
            for query in self._queries.__dict__().values()
        ]

    def to_json(self) -> str:
        """
        Serializes the UMLSL_queries instance to a JSON string.
        """
        import json
        return json.dumps(self.to_dict(), indent=2)

    def clear(self) -> None:
        """Remove all queries."""
        for query_id in list(self._queries.__dict__().keys()):
            self._queries.pop(query_id)

    def from_dict(self, data: list[dict[str, Any]]) -> None:
        """
        Loads queries from a list of dictionaries.

        Args:
            data: A list containing query dictionaries.
        """
        if not isinstance(data, list):
            raise ValueError("Queries payload must be a list.")
        self.clear()
        for entry in data:
            if not isinstance(entry, dict):
                raise ValueError("Each query must be a dictionary.")
            params = UMLSLQueryParams(
                latex=entry["latex"],
                assigned_car_uid=entry["assigned_car_uid"],
            )
            query = UMLSLQuery.from_params(params)
            if "uid" in entry:
                query.uid = entry["uid"]
            self.add_umlsl_query(query)

    def from_json(self, json_string: str) -> None:
        """
        Loads queries from a JSON string.

        Args:
            json_string: A JSON-formatted string containing umlsl query data.
        """
        import json
        data = json.loads(json_string)
        self.from_dict(data)
