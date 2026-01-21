from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import View
from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser
from pse.umlsl_editor.src.query.interval import Interval
from pse.umlsl_editor.src.query.lexer import Lexer


class UMLSLEvaluator:
    """Facade for the UI to interact with logic."""

    def __init__(self, traffic_snapshot: TrafficSnapshotModel):
        self._traffic_snapshot = traffic_snapshot

    def evaluate_query(self, latex_string: str, car: Car, braking_accel: float) -> bool:
        tokens = Lexer(latex_string).tokenize()
        ast = ASTParser(tokens, self._traffic_snapshot.get_cars()).parse_ast()

        views = self._compute_views(car, braking_accel)
        for view in views:
            if ast.evaluate(self._traffic_snapshot, view, []):
                return True

        return False

    def _compute_views(self, car: Car, braking_accel: float) -> list[View]:
        max_v = self._traffic_snapshot.get_max_velocity()
        horizon = max_v * max_v / (2.0 * braking_accel)

        horizontal_extension = Interval(
            car.absolute_position() - horizon,
            car.absolute_position() + horizon
        )
        # todo: depending on next turn intent, compute multi-views (Fig 6 and Fig 3 in paper)
        lanes = []  # todo
        return [View(lanes, horizontal_extension, car)]
