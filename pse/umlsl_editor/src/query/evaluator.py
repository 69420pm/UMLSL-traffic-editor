from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast import EvaluationContext
from pse.umlsl_editor.src.query.ast_parser import ASTParser
from pse.umlsl_editor.src.query.token import Lexer


class UMLSLEvaluator:
    """Facade for the UI to interact with logic."""

    def __init__(self):
        self.evaluator = Evaluator()

    def evaluate_query(self, latex_string: str, snapshot: TrafficSnapshot, view: Car) -> bool:
        tokens = Lexer(latex_string).tokenize()
        ast = ASTParser(tokens).parse_ast()

        context = EvaluationContext(snapshot, view)
        raise ast.evaluate(context)

    def validate_syntax(self, latex_string: str) -> bool:
        raise NotImplementedError




class Evaluator:
    pass
