from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQueryParams
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel


class EditUMLSLQuery(Command[None]):
    """Edits an existing UMLSL query in the UMLSL editor."""

    def __init__(self, query_id: str, umlsl_query_params: UMLSLQueryParams, umlsl_queries: UMLSLQueriesModel):
        """
        Initialize the EditUMLSLQuery command with the query identifier and new content.

        Args:
            query_id: Unique identifier of the UMLSL query to be edited.
            umlsl_query_params: New UMLSLQuery params to update the existing query.
            umlsl_queries: UmlslQueries manager.
        """
        self.query_id = query_id
        self.umlsl_query_params = umlsl_query_params
        self._umlsl_queries = umlsl_queries

    def execute(self) -> None:
        """
        Edits the specified UMLSL query in the UMLSL editor.

        Raises:
            CommandValidationError: If command validation fails.
        """
        query = self._umlsl_queries.get_query_by_id(self.query_id)
        self._umlsl_queries.update_umlsl_query(query, self.umlsl_query_params)
        raise NotImplementedError("Prototype Method")