from pse.umlsl_editor.src.core.dataclasses.car import Car
from pse.umlsl_editor.src.core.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import Interval, View
from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser
from pse.umlsl_editor.src.query.lexer import Lexer


def parse_latex_string(latex_string: str):
    tokens = Lexer(latex_string).tokenize()
    return ASTParser(tokens).parse_ast()


class UMLSLEvaluator:
    """Facade for the UI to interact with logic."""

    def __init__(self, braking_accel: float):
        self.braking_accel = braking_accel

    def evaluate_query(self, latex_string: str, traffic_snapshot: TrafficSnapshot, car: Car) -> bool:
        ast = parse_latex_string(latex_string)

        horizon = self.compute_horizon(car)
        horizontal_extension = Interval(car.absolute_position() - horizon, car.absolute_position() + horizon)
        lanes = []  # todo

        view = View(lanes, horizontal_extension, car)
        raise ast.evaluate(traffic_snapshot, view)

    def compute_horizon(self, car: Car) -> float:
        return (car.velocity * car.velocity) / (2.0 * self.braking_accel)
