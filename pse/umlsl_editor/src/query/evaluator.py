from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.view_models.traffic_snapshot import TrafficSnapshot
from pse.umlsl_editor.src.query.ast.ast import View
from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser
from pse.umlsl_editor.src.query.interval import Interval
from pse.umlsl_editor.src.query.lexer import Lexer


class UMLSLEvaluator:
    """Facade for the UI to interact with logic."""

    def __init__(self, traffic_snapshot: TrafficSnapshot, braking_accel: float):
        self.braking_accel = braking_accel
        self.traffic_snapshot = traffic_snapshot

    def _compute_horizon(self) -> float:
        braking_distances = map(
            lambda car: car.velocity * car.velocity / (2.0 * self.braking_accel),
            self.traffic_snapshot.get_cars()
        )
        return max(braking_distances)

    def evaluate_query(self, latex_string: str, car: Car) -> bool:
        ast = self.parse_latex_string(latex_string)
        horizon = self.compute_horizon()
        horizontal_extension = Interval(
            car.absolute_position() - horizon,
            car.absolute_position() + horizon
        )
        views = self.compute_views(car, horizontal_extension)

        for view in views:
            if ast.evaluate(self.traffic_snapshot, view, car):
                return True

        return False

    def parse_latex_string(self, latex_string: str):
        tokens = Lexer(latex_string).tokenize()
        return ASTParser(tokens, self.traffic_snapshot).parse_ast()

    def compute_horizon(self):
        max_v = self.traffic_snapshot.get_max_velocity()
        return max_v * max_v / (2.0 * self.braking_accel)

    def compute_views(self, car: Car, horizontal_extension) -> list[View]:
        # todo: depending on next turn intent, compute multi-views (Fig 6 and Fig 3 in paper)
        lanes = []  # todo
        return [View(lanes, horizontal_extension, car)]
