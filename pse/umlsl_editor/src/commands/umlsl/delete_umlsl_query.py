from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel


class DeleteUMLSLQuery(Command[None]):
    """Deletes a UMLSL query from the UMLSL editor."""

    def __init__(self, query_id: str, umlsl_queries: UMLSLQueriesModel):
        """
        Initialize the DeleteUMLSLQuery command with the query identifier.

        Args:
            query_id: Unique identifier of the UMLSL query to be deleted.
            umlsl_queries: UmlslQueries manager.
        """
        self._query_id = query_id
        self._umlsl_queries = umlsl_queries

    def execute(self) -> None:
        """
        Deletes the specified UMLSL query from the UMLSL editor.

        Raises:
            CommandValidationError: If command validation fails.
        """
        #TODO: Error Handling
        self._umlsl_queries.remove_umlsl_query(self._query_id)
        raise NotImplementedError("Prototype Method")