from typing import Optional

from pse.umlsl_editor.car import Car
from pse.umlsl_editor.query.nodes import ConjunctionNode, HorizontalChopNode, AtomNode
from pse.umlsl_editor.query.token import Lexer
from pse.umlsl_editor.traffic_snapshot import TrafficSnapshot

class UMLSLEvaluator:
    """Facade for the UI to interact with logic."""
    def __init__(self):
        self.lexer = Lexer()
        self.evaluator = Evaluator()

    def evaluate_query(self, latex_string: str, snapshot: TrafficSnapshot) -> bool:
        pass

    def validate_syntax(self, latex_string: str) -> bool:
        pass

class EvaluationContext:
    """Context passed down during evaluation."""
    def __init__(self, snapshot: TrafficSnapshot, view_car: Optional[Car] = None):
        self.snapshot = snapshot
        self.view_car = view_car  # The 'perspective' car for spatial logic

class Evaluator:
    """Visitor that evaluates the AST against the Context."""
    def visit_conjunction(self, node: ConjunctionNode, ctx: EvaluationContext) -> bool:
        pass

    def visit_chop(self, node: HorizontalChopNode, ctx: EvaluationContext) -> bool:
        # Complex logic splitting the view into two
        pass

    def visit_atom(self, node: AtomNode, ctx: EvaluationContext) -> bool:
        pass
