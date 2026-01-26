from dataclasses import dataclass

from pse.umlsl_editor.src.model.entities.entity import Entity
from pse.umlsl_editor.src.model.helper.uid_service import generate_uid


class UMLSLQueryValidationError(ValueError):
    """
    Custom exception raised when UMLSLQuery validation fails.
    """
    pass


@dataclass(frozen=True)
class UMLSLQueryParams:
    """
    Dataclass representing parameters for creating a UMLSL query.

    Attributes:
        latex (str): The UMLSL query in LaTeX format.
        assigned_car_name (str): The name of the car associated with the query.
        validation (bool): A flag indicating whether the query is true of false in the current context
    """
    latex: str
    assigned_car_name: str
    validation: bool

@dataclass()
class UMLSLQuery(Entity):
    """Dataclass representing a UMLSL query.

    Attributes:
        uid (str): The unique identifier of the UMLSL query.
        latex (str): The UMLSL query in LaTeX format.
        assigned_car_name (str): The name of the car associated with the query.
        validation (bool): A flag indicating whether the query is true of false in the current context.

    Raises:
        UMLSLQueryValidationError: If any validation check fails.
    """
    latex: str
    assigned_car_name: str
    validation: bool

    @classmethod
    def from_params(cls, params: UMLSLQueryParams) -> "UMLSLQuery":
        """
        Creates a UMLSLQuery instance from a UMLSLQueryParams dataclass.

        Args:
            params: UMLSLQueryParams instance containing all UMLSL query attributes.
        """
        return cls(
            uid=generate_uid(),
            latex=params.latex,
            assigned_car_name=params.assigned_car_name,
            validation=params.validation
        )

    def update_from_params(self, params: UMLSLQueryParams) -> None:
        """
        Updates the UMLSLQuery instance's attributes based on a UMLSLQueryParams object.

        Args:
            params: An instance of UMLSLQueryParams containing the new UMLSL query attributes.
        """
        self.latex = params.latex
        self.assigned_car_name = params.assigned_car_name
        self.validation = params.validation
        self.__post_init__()

    def __post_init__(self) -> None:
        """
        Validates the UMLSLQuery instance after initialization.

        Raises:
            UMLSLQueryValidationError: If any validation check fails.
        """
        self.validate()
        self._initialized = True

    def __setattr__(self, name: str, value: object) -> None:
        super().__setattr__(name, value)
        if getattr(self, "_initialized", False):
            self.validate()

    def validate(self) -> None:
        if not isinstance(self.latex, str) or not self.latex.strip():
            raise UMLSLQueryValidationError("Latex query must be a non-empty string.")

        if not isinstance(self.assigned_car_name, str) or not self.assigned_car_name.strip():
            raise UMLSLQueryValidationError("Assigned car name must be a non-empty string.")

        if not isinstance(self.validation, bool):
            raise UMLSLQueryValidationError("Validation must be a boolean.")

