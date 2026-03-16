from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_model import TrafficSnapshotModel
from pse.umlsl_editor.src.model.domain_models.traffic_snapshot_reader import TrafficSnapshotReader
from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.model.interval import Interval
from pse.umlsl_editor.src.model.traffic_value_objects.segments.segment import Segment
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

    def evaluate_query(self, query_text: str, car: Car, ts: TrafficSnapshotModel) -> QueryResult:
        ast = self._parse_ast(query_text)
        horizontal_horizon = car.environment.horizontal_horizon

        for virtual_lanes in car.environment.parallel_virtual_lanes:
            def translate_coordinate_system(func) -> dict[str, dict[Segment, Interval]]:
                translated: dict[str, dict[Segment, Interval]] = {}
                for traffic_snapshot_car in ts.get_car_list():
                    translated[traffic_snapshot_car.uid] = car.environment.translate_interval_coordinates(
                        virtual_lanes,
                        horizontal_horizon,
                        func(traffic_snapshot_car),
                        traffic_snapshot_car,
                        ts
                    )
                return translated

            # translate physical, reserved and claimed intervals of every car into the coordinate system of ego
            intersecting_cars: dict[str, dict[Segment, Interval]] = translate_coordinate_system(
                lambda c: c.environment.physical_segment_intervals)
            print("reserved segments:")
            reserved_segments: dict[str, dict[Segment, Interval]] = translate_coordinate_system(
                lambda c: c.environment.reserved)
            claimed_segments: dict[str, dict[Segment, Interval]] = translate_coordinate_system(
                lambda c: c.environment.claimed
            )

            print("evaluating parallel virtual lane with:")
            print("intersecting cars: ")
            for intersecting_car in intersecting_cars:
                print(">", ts.cars[intersecting_car].name, ":")
                for segment, interval in intersecting_cars[intersecting_car].items():
                    print(f"  {ts.get_segment_info(segment.uid)}: {interval}")
            print("")
            print("reserved cars: ")
            for intersecting_car in reserved_segments:
                print(">", ts.cars[intersecting_car].name, ":")
                for segment, interval in reserved_segments[intersecting_car].items():
                    print(f"  {ts.get_segment_info(segment.uid)}: {interval}")
            view = View(
                virtual_lanes,
                horizontal_horizon,
                car,
                intersecting_cars,
                reserved_segments,
                claimed_segments,
            )
            result = ast.evaluate(self._traffic_snapshot, view, dict())
            # We demand that there exists a view that evaluates true
            if result:
                return QueryResult(query_text, True)

        return QueryResult(query_text, False)


class ParserError(Exception):
    def __init__(
            self,
            ast_parser_error: ASTParserError,
            input: str,
            tokens: list[Token],
            scope_1: int,
            scope_2: int,
    ):
        super().__init__(ast_parser_error)
        scope_start = min(scope_1, scope_2)
        scope_end = max(scope_1, scope_2)

        self.input = input
        self.reason = ast_parser_error.reason
        self.help = ast_parser_error.help

        if scope_start >= len(tokens):
            # ASTParser expects new tokens only after the input
            # we indicate this by starting the error after the input
            self.scope_start = len(input) + 1
            self.scope_end = len(input) + 4
        elif scope_end >= len(tokens):
            # ASTParser expects a token after the end of the input, but the starting token is still in bounds
            self.scope_start = tokens[scope_start].start_index
            self.scope_end = len(input) + 3
        else:
            self.scope_start = tokens[scope_start].start_index
            self.scope_end = tokens[scope_end].end_index
