from dataclasses import dataclass

from PySide6.QtCore import Signal

from pse.umlsl_editor.src.core.entities.umlsl_query import UMLSLQuery

class UMLSLQueriesValidationError(Exception):
    """Raised when UMLSL queries validation fails in the context of a traffic snapshot."""
    pass

@dataclass
class UmlslQueries:
    queries: list[UMLSLQuery]

    umlsl_query_added = Signal(UMLSLQuery)
    umlsl_query_removed = Signal(UMLSLQuery)
    umlsl_query_updated = Signal(UMLSLQuery)

    def add_umlsl_query(self, umlsl_query: UMLSLQuery) -> None:
        """
        Adds a UMLSL query to the snapshot and validates all attributes in the context of the snapshot.
        Raises:
            TrafficSnapshotValidationError: If the UMLSL query is invalid in the context of the snapshot.
        """
        raise NotImplementedError

    def remove_umlsl_query(self, umlsl_query: UMLSLQuery) -> None:
        """
        Removes a UMLSL query from the snapshot.
        """
        raise NotImplementedError()

    def update_umlsl_query(self, umlsl_query_data: UMLSLQuery) -> None:
        """
        Updates an existing UMLSL query in the snapshot and validates all attributes in the context of the snapshot.

        Raises:
            UMLSLQueriesValidationError: If the updated UMLSL query is invalid in the context of the snapshot.
        """
        raise NotImplementedError