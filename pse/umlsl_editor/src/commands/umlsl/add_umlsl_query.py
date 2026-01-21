from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQuery, UMLSLQueryParams
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel


class AddUMLSLQuery(Command[None]):
    """Adds a new UMLSL query to the UMLSL editor."""

    def __init__(self, umlsl_query_params: UMLSLQueryParams, umlsl_queries: UMLSLQueriesModel):
        """
        Initialize the AddUMLSLQuery command with the query and the list of UMLSL queries.

        Args:
            umlsl_query_params: UMLSLQuery params to create an object.
            umlsl_queries: UmlslQueries manager.
        """
        self._umlsl_query = umlsl_query_params
        self._umlsl_queries = umlsl_queries

    def execute(self) -> None:
        """
        Adds the specified UMLSL query to the list of UMLSL queries.

        Raises:
            CommandValidationError: If command validation fails.
        """
        raise NotImplementedError