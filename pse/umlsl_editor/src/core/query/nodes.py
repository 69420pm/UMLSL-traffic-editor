from abc import abstractmethod, ABC

from pse.umlsl_editor.src.core.query.evaluator import EvaluationContext


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
    def __init__(self, child: ASTNode):
        self.child = child


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


class NegationNode(UnaryOpNode):
    def evaluate(self, context: EvaluationContext) -> bool:
        return not self.child.evaluate(context)
