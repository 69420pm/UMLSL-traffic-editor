from abc import abstractmethod, ABC
from typing import Optional

from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot


class EvaluationContext:
    """Context passed down during evaluation."""

    def __init__(self, snapshot: TrafficSnapshot, view_car: Optional[Car] = None):
        self.snapshot = snapshot
        self.view_car = view_car  # The 'perspective' car for spatial logic


class ASTNode(ABC):
    """Abstract Syntax Tree Base Node."""

    @abstractmethod
    def evaluate(self, context: EvaluationContext) -> bool:
        pass


class AtomNode(ASTNode):
    """Represents logic like 're(c1)' or 'safe'."""

    # todo: too dumb to implement rn

    def __init__(self, raw_text: str):
        self.raw_text = raw_text


class BinaryOpNode(ASTNode, ABC):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right


class UnaryOpNode(ASTNode, ABC):
    def __init__(self):
        pass


class ConjunctionNode(BinaryOpNode):
    def evaluate(self, context: EvaluationContext) -> bool:
        return self.left.evaluate(context) and self.right.evaluate(context)


class DisjunctionNode(BinaryOpNode):
    def evaluate(self, context: EvaluationContext) -> bool:
        return self.left.evaluate(context) or self.right.evaluate(context)


class HorizontalChopNode(BinaryOpNode):
    def evaluate(self, context: EvaluationContext) -> bool:
        # todo: implement horizontal chop
        pass


class VerticalChopNode(BinaryOpNode):
    def evaluate(self, context: EvaluationContext) -> bool:
        # todo: implement horizontal chop
        pass


class TrueNode(UnaryOpNode):
    def evaluate(self, context: EvaluationContext) -> bool:
        return True


class NegationNode(UnaryOpNode):
    def __init__(self, child: ASTNode):
        super().__init__()
        self.child = child

    def evaluate(self, context: EvaluationContext) -> bool:
        return not self.child.evaluate(context)
