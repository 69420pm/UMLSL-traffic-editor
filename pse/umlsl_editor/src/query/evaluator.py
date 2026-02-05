from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import View
from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser
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
        ast = ASTParser(tokens, self._traffic_snapshot.get_car_list()).parse_ast()
        return ast.to_latex()

    def evaluate_query(self, query: str, car: Car) -> QueryResult:
        tokens = Lexer(query).tokenize()
        ast = ASTParser(tokens, self._traffic_snapshot.get_car_list()).parse_ast()

        space_interval = car.environment.space_interval
        for virtual_lanes in car.environment.parallel_virtual_lanes:
            view = View(virtual_lanes, space_interval, car)
            result = ast.evaluate(self._traffic_snapshot, view, [])
            # We demand that there exists a view that evaluates true
            if result:
                return QueryResult(query, True)

        return QueryResult(query, False)
