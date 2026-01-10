from abc import abstractmethod, ABC
from enum import IntEnum

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.view import View


# Assigns a value to each AST Node
# Higher value = binds tighter (evaluated first)
class Precedence(IntEnum):
    NULLARY = 50  # Nullary Nodes
    UNARY = 40
    BINARY_CONJUNCTION = 30  # And
    BINARY_DISJUNCTION = 20  # Or
    BINARY_CHOP = 10  # Horizontal Chop, Vertical Chop
    LOWEST = 0


class PrecedenceText:
    def __init__(self, precedence: int, text: str):
        self.precedence = precedence
        self.text = text


class ASTNode(ABC):
    """Abstract Syntax Tree Base Node."""

    # variable_car_map maps the car's variable to its value
    @abstractmethod
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        pass

    @abstractmethod
    def to_precedence_latex(self) -> PrecedenceText:
        pass


class NullaryNode(ASTNode, ABC):
    def __init__(self, latex_code):
        self.precedence = Precedence.NULLARY
        self.latex_code = latex_code
        pass

    def to_precedence_latex(self) -> PrecedenceText:
        return PrecedenceText(self.precedence, self.latex_code)


class UnaryNode(ASTNode, ABC):
    def __init__(self, child: ASTNode):
        self.precedence = Precedence.UNARY
        self.child = child

    @abstractmethod
    def to_latex(self, child: str) -> str:
        pass

    def to_precedence_latex(self) -> PrecedenceText:
        child_precedence_text = self.child.to_precedence_latex()
        child_precedence = child_precedence_text.precedence
        child_text = child_precedence_text.text

        # For example, NOT (A AND B) -> NOT has precedence over AND -> add parentheses
        if self.precedence > child_precedence:
            child_text = f"\\({child_text}\\)"

        return PrecedenceText(self.precedence, self.to_latex(child_text))


class BinaryNode(ASTNode, ABC):
    def __init__(self, precedence: int, left: ASTNode, right: ASTNode):
        self.precedence = precedence
        self.left = left
        self.right = right

    def to_precedence_latex(self) -> PrecedenceText:
        left_precedence_text = self.left.to_precedence_latex()
        right_precedence_text = self.right.to_precedence_latex()

        left_text = left_precedence_text.text
        if self.precedence > left_precedence_text.precedence:
            left_text = f"\\({left_precedence_text.text}\\)"

        right_text = right_precedence_text.text
        if self.precedence > right_precedence_text.precedence:
            right_text = f"\\({right_precedence_text.text}\\)"

        return PrecedenceText(self.precedence, self.to_latex(left_text, right_text))

    @abstractmethod
    def to_latex(self, left: str, right: str) -> str:
        pass
