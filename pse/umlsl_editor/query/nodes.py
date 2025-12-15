from abc import abstractmethod, ABC

class ASTNode(ABC):
    """Abstract Syntax Tree Base Node."""
    @abstractmethod
    def accept(self, visitor: 'Evaluator'):
        pass

class BinaryOpNode(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

class UnaryOpNode(ASTNode):
    def __init__(self, child: ASTNode):
        self.child = child

# Concrete AST Nodes
class ConjunctionNode(BinaryOpNode): pass
class DisjunctionNode(BinaryOpNode): pass
class HorizontalChopNode(BinaryOpNode): pass
class VerticalChopNode(BinaryOpNode): pass
class NegationNode(UnaryOpNode): pass

class AtomNode(ASTNode):
    """Represents logic like 're(c1)' or 'safe'."""
    def __init__(self, raw_text: str):
        self.raw_text = raw_text