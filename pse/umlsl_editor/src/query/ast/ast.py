from abc import abstractmethod, ABC
from enum import IntEnum

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.view import View


# Assigns a value to each AST Node
# Higher value = binds tighter (evaluated first)
class Precedence(IntEnum):
    ATOM = 50  # Nullary Nodes
    UNARY = 40
    BINARY_CHOP = 30  # Horizontal Chop, Vertical Chop
    BINARY_CONJUNCTION = 20  # And
    BINARY_DISJUNCTION = 10  # Or


class LaTexFragment:
    def __init__(self, precedence: int, text: str):
        self.precedence = precedence
        self.text = text


class ASTNode(ABC):
    """Abstract Syntax Tree Base Node."""

    @abstractmethod
    def evaluate(self, traffic_snapshot: TrafficSnapshot, view: View, variable_car_map: dict[str, Car]) -> bool:
        pass

    def to_latex(self) -> str:
        return self._render().text

    @abstractmethod
    def _render(self) -> LaTexFragment:
        pass


class AtomNode(ASTNode, ABC):
    def __init__(self, latex_code):
        self._precedence = Precedence.ATOM
        self._latex_code = latex_code
        pass

    def _render(self) -> LaTexFragment:
        return LaTexFragment(self._precedence, self._latex_code)


class UnaryNode(ASTNode, ABC):
    def __init__(self, child: ASTNode):
        self._precedence = Precedence.UNARY
        self._child = child

    def _render(self) -> LaTexFragment:
        child_precedence_text = self._child._render()
        child_precedence = child_precedence_text.precedence
        child_text = child_precedence_text.text

        # For example, NOT (A AND B) -> NOT has precedence over AND -> add parentheses
        if self._precedence > child_precedence:
            child_text = f"\\({child_text}\\)"

        return LaTexFragment(self._precedence, self._format(child_text))

    @abstractmethod
    def _format(self, child: str) -> str:
        pass


class BinaryNode(ASTNode, ABC):
    def __init__(self, precedence: int, left: ASTNode, right: ASTNode):
        self._precedence = precedence
        self._left = left
        self._right = right

    def _render(self) -> LaTexFragment:
        left_precedence_text = self._left._render()
        right_precedence_text = self._right._render()

        left_text = left_precedence_text.text
        if self._precedence > left_precedence_text.precedence:
            left_text = f"\\({left_precedence_text.text}\\)"

        right_text = right_precedence_text.text
        if self._precedence > right_precedence_text.precedence:
            right_text = f"\\({right_precedence_text.text}\\)"

        return LaTexFragment(self._precedence, self._format(left_text, right_text))

    @abstractmethod
    def _format(self, left: str, right: str) -> str:
        pass
