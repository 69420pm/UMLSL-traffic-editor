from abc import abstractmethod, ABC
from enum import IntEnum
from typing import TYPE_CHECKING

from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.view import View

if TYPE_CHECKING:
    from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel


# Assigns a value to each AST Node
# Higher value = binds tighter (evaluated first)
class Precedence(IntEnum):
    ATOM = 50  # Nullary Nodes
    UNARY = 40
    UNARY_EQUALITY = 35
    BINARY_CHOP = 30  # Horizontal Chop, Vertical Chop
    BINARY_CONJUNCTION = 20  # And
    BINARY_DISJUNCTION = 10  # Or
    UNARY_QUANTOR = 0


class ASTNode(ABC):
    """Abstract Syntax Tree Base Node."""

    def __init__(self, precedence: Precedence):
        self._precedence = precedence

    @abstractmethod
    def evaluate(self, traffic_snapshot: TrafficSnapshotModel, view: View, variable_car_map: dict[str, Car]) -> bool:
        pass

    @abstractmethod
    def to_latex(self) -> str:
        pass


class AtomNode(ASTNode, ABC):
    def __init__(self, latex_code):
        super().__init__(Precedence.ATOM)
        self._latex_code = latex_code
        pass

    def to_latex(self) -> str:
        return self._latex_code


class UnaryNode(ASTNode, ABC):
    def __init__(self, child: ASTNode):
        super().__init__(Precedence.UNARY)
        self._child = child

    def to_latex(self) -> str:
        child_text = self._child.to_latex()

        # For example, NOT (A AND B) -> NOT has precedence over AND -> add parentheses
        if self._precedence > self._child._precedence:
            child_text = f"\\left({child_text}\\right)"

        return self._format(child_text)

    @abstractmethod
    def _format(self, child: str) -> str:
        pass


class BinaryNode(ASTNode, ABC):
    def __init__(self, precedence: Precedence, left: ASTNode, right: ASTNode):
        super().__init__(precedence)
        self._left = left
        self._right = right

    def to_latex(self) -> str:
        left_text = self._left.to_latex()
        right_text = self._right.to_latex()

        if self._precedence > self._left._precedence:
            left_text = f"\\left({left_text}\\right)"

        if self._precedence > self._right._precedence:
            right_text = f"\\left({right_text}\\right)"

        return self._format(left_text, right_text)

    @abstractmethod
    def _format(self, left: str, right: str) -> str:
        pass
