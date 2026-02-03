from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.query.ast.ast import View
from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.query.lexer import Lexer


class QueryResult:
    def __init__(self, latex_code: str, holds: bool):
        self.holds = holds
        self.latex_code = latex_code


class UMLSLEvaluator:
    def __init__(self, traffic_snapshot: TrafficSnapshotModel):
        self._traffic_snapshot = traffic_snapshot

    def compute_latex(self, latex_string: str) -> str:
        tokens = Lexer(latex_string).tokenize()
        ast = ASTParser(tokens, self._traffic_snapshot.get_cars()).parse_ast()
        return ast.to_latex()

    def evaluate_query(self, query: str, car: Car, braking_accel: float) -> QueryResult:
        tokens = Lexer(query).tokenize()
        ast = ASTParser(tokens, self._traffic_snapshot.get_cars()).parse_ast()

        max_v = self._traffic_snapshot.get_max_velocity()
        horizon = max_v * max_v / (2.0 * braking_accel)
        horizontal_extension = Interval(
            car.absolute_position() - horizon,
            car.absolute_position() + horizon
        )
        view = View(car.car_environment.virtual_lanes, horizontal_extension, car)

        latex_string = ast.to_latex()
        query_holds = ast.evaluate(self._traffic_snapshot, view, [])

        return QueryResult(latex_string, query_holds)