from dataclasses import dataclass

from pse.umlsl_editor.src.core.dataclasses.car import Car


@dataclass
class UMLSLQuery:
    latex: str
    assigned_car: Car
    validation: bool