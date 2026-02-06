from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import View, ASTNode
from pse.umlsl_editor.src.query.ast.ast_parser import ASTParser, ASTParserError
from pse.umlsl_editor.src.query.lexer import Lexer, Token


class QueryResult:
    def __init__(self, latex_code: str, holds: bool):
        self.holds = holds
        self.latex_code = latex_code


class UMLSLEvaluator:
    def __init__(self, traffic_snapshot: TrafficSnapshotReader):
        self._traffic_snapshot = traffic_snapshot

    def _parse_ast(self, latex_string: str) -> ASTNode:
        tokens = Lexer(latex_string).tokenize()
        try:
            return ASTParser(tokens, self._traffic_snapshot.get_car_list()).parse_ast()
        except ASTParserError as e:
            raise ParserError(e, latex_string, tokens, e.scope_start, e.scope_end)

    def compute_latex(self, latex_string: str) -> str:
        return self._parse_ast(latex_string).to_latex()

    def evaluate_query(self, query: str, car: Car) -> QueryResult:
        ast = self._parse_ast(query)
        space_interval = car.environment.space_interval
        for virtual_lanes in car.environment.parallel_virtual_lanes:
            view = View(virtual_lanes, space_interval, car)
            result = ast.evaluate(self._traffic_snapshot, view, [])
            # We demand that there exists a view that evaluates true
            if result:
                return QueryResult(query, True)

        return QueryResult(query, False)


class ParserError(Exception):
    def __init__(
            self,
            ast_parser_error: ASTParserError,
            input: str,
            tokens: list[Token],
            scope_start: int,
            scope_end: int,
    ):
        super().__init__(ast_parser_error)

        self.input = input
        self.reason = ast_parser_error.args[0]
        self.scope_start = tokens[scope_start].start_index
        self.scope_end = tokens[scope_end].end_index
