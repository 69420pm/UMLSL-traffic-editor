from pse.umlsl_editor.src.commands.command import Command
from pse.umlsl_editor.src.model.domain_models.umlsl_queries import UMLSLQueries


class DeleteUMLSLQuery(Command[None]):
    """Deletes a UMLSL query from the UMLSL editor."""

    def __init__(self, query_id: str, umlsl_queries: UMLSLQueries):
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
        raise NotImplementedError