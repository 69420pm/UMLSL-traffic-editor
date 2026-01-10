from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import View
from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser
from pse.umlsl_editor.src.query.interval import Interval
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
        views = self.compute_views(traffic_snapshot, car)

        for view in views:
            if ast.evaluate(traffic_snapshot, view, car):
                return True

        return False

    def compute_views(self, traffic_snapshot: TrafficSnapshot, car: Car) -> list[View]:
        # todo: depending on next turn intent, compute multi-views (Fig 6 and Fig 3 in paper)
        horizon = self.compute_horizon(car)
        horizontal_extension = Interval(car.absolute_position() - horizon, car.absolute_position() + horizon)
        lanes = []  # todo
        return [View(lanes, horizontal_extension, car)]

    def compute_horizon(self, car: Car) -> float:
        return (car.velocity * car.velocity) / (2.0 * self.braking_accel)
