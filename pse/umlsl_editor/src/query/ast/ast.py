from abc import abstractmethod, ABC

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot, Path
from pse.umlsl_editor.src.query.view import View


class ASTNode(ABC):
    """Abstract Syntax Tree Base Node."""

    # variable_car_map maps the car's variable to its value
    @abstractmethod
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        pass


class NullaryNode(ASTNode, ABC):
    def __init__(self):
        pass


class UnaryNode(ASTNode, ABC):
    def __init__(self, child: ASTNode):
        self.child = child


class BinaryNode(ASTNode, ABC):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right
