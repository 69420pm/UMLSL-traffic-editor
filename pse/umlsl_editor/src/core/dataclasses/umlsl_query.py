from dataclasses import dataclass

from pse.umlsl_editor.src.core.dataclasses.car import Car


@dataclass()
class UMLSLQuery:
    """Dataclass representing a UMLSL query.

    Attributes:
        uid (str): The unique identifier of the UMLSL query.
        latex (str): The UMLSL query in LaTeX format.
        assigned_car_name (str): The name of the car associated with the query.
        validation (bool): A flag indicating whether the query is true of false in the current context.
    """
    uid: str
    latex: str
    assigned_car_name: str
    validation: bool

    def __eq__(self, other):
        """Checks equality based only on the unique identifier (uid) of the UMLSL query."""
        if not isinstance(other, UMLSLQuery):
            return NotImplemented
        return self.uid == other.uid

    def __hash__(self):
        """Generates a hash based only on the unique identifier (uid) of the UMLSL query."""
        return hash(self.uid)