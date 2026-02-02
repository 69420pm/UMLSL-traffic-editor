from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.umlsl_queries_model import UMLSLQueriesModel
from pse.umlsl_editor.src.model.entities.umlsl_query import UMLSLQueryParams


class EditUMLSLQuery(Command[None]):
    """Edits the properties of an existing UMLSL query in the model."""

    def __init__(
            self,
            query_id: str,
            umlsl_query_params: UMLSLQueryParams,
            umlsl_queries_model: UMLSLQueriesModel
    ):
        """
        Initialize the EditUMLSLQuery command.

        Args:
            query_id: Unique identifier of the query to be edited.
            umlsl_query_params: Parameters containing the updates.
            umlsl_queries_model: The model containing the query.
        """
        self.query_id = query_id
        self.umlsl_query_params = umlsl_query_params
        self.umlsl_queries_model = umlsl_queries_model

    def execute(self) -> None:
        """
        Edits the properties of the query with the specified unique identifier.

        Raises:
            UMLSLQueriesValidationError: If the query does not exist.
        """

        query = self.umlsl_queries_model.get_query_by_id(self.query_id)
        self.umlsl_queries_model.update_umlsl_query(query, self.umlsl_query_params)
