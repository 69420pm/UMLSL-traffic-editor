from typing import Optional

from pse.umlsl_editor.src.core.car import Car
from pse.umlsl_editor.src.core.query.token import Lexer
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot


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
    pass
