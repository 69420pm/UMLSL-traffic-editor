from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import ASTNode
from pse.umlsl_editor.src.query.ast.car_resolve import ConstantCarResolve, VariableCarResolve, CarResolve
from pse.umlsl_editor.src.query.ast.chop_node import HorizontalChopNode, VerticalChopNode
from pse.umlsl_editor.src.query.ast.claim_node import ClaimNode
from pse.umlsl_editor.src.query.ast.crossing_node import CrossingSegmentNode
from pse.umlsl_editor.src.query.ast.equality_node import EqualityCarNode
from pse.umlsl_editor.src.query.ast.free_node import FreeNode
from pse.umlsl_editor.src.query.ast.logic_node import ConjunctionNode, DisjunctionNode, NegationNode, TrueNode
from pse.umlsl_editor.src.query.ast.quantor_node import ExistsNode, ForallNode
from pse.umlsl_editor.src.query.ast.reserve_node import ReserveNode
from pse.umlsl_editor.src.query.lexer import Token, TokenType


class ASTParser:
    def __init__(self, tokens: list[Token], cars: list[Car]):
        self._tokens = tokens
        self._cars = cars

    def parse_ast(self):
        if not self._tokens:
            raise SyntaxError("Empty token list")
        return self.parse_ast_rec(0, len(self._tokens) - 1, [])

    def parse_ast_rec(self, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        if start > end:
            raise ASTParserError(
                "expected expression here",
                min(start, end + 1),
                start
            )

        tokens = self._tokens

        # todo: parse <phi> (Somewhere Node)

        height = 0
        split_index = -1
        # we need a value that is bigger than all others, in python there is no "max_int"
        min_precedence = float('inf')

        for i in range(start, end + 1):
            token = tokens[i]

            if height == 0 and token.type in {TokenType.EXITS, TokenType.FORALL}:
                break

            if token.type in {TokenType.L_PAREN, TokenType.L_CURLY}:
                height += 1
            elif token.type in {TokenType.R_PAREN, TokenType.R_CURLY}:
                height -= 1
            elif height == 0 and token.type.is_infix_binary_op:
                precedence = token.type.get_infix_binary_op_precedence()
                # Find the operator with the lowest binding (left-associativity)
                if precedence <= min_precedence:
                    min_precedence = precedence
                    split_index = i

        if height != 0:
            raise ASTParserError(
                "unbalanced parentheses",
                start,
                end,
                "Considering adding/removing ')' or '}'"
            )

        if split_index != -1:
            return self.parse_infix(start, end, split_index, declared_variables)

        if tokens[start].type == TokenType.L_PAREN and tokens[end].type == TokenType.R_PAREN:
            return self.parse_ast_rec(start + 1, end - 1, declared_variables)

        return self.parse_prefix(start, end, declared_variables)

    def parse_infix(self, start: int, end: int, split_index: int, declared_variables: list[str]) -> ASTNode:
        token = self._tokens[split_index]
        token_type = token.type

        if not (start < split_index < end <= len(self._tokens) - 1):
            if not start < split_index:
                raise ASTParserError(
                    f"missing first argument",
                    start,
                    split_index,
                    f"Consider adding an argument before '{token_type.value}'"
                )
            else:
                scope_end = len(self._tokens) if end == len(self._tokens) - 1 else end
                raise ASTParserError(
                    f"missing second argument",
                    split_index,
                    scope_end,
                    f"Consider adding an argument after '{token_type.value}'"
                )

        if token_type == TokenType.CAR_EQUALS:
            if start != split_index - 1 or end != split_index + 1:
                raise ASTParserError(
                    "expected car names as arguments",
                    start,
                    end,
                    "Consider writing the equality as 'a = b', where a and b are car names or variables"
                )
            car1 = self.parse_car(start, declared_variables)
            car2 = self.parse_car(end, declared_variables)
            return EqualityCarNode(car1, car2)
        else:
            left_ast = self.parse_ast_rec(start, split_index - 1, declared_variables)
            right_ast = self.parse_ast_rec(split_index + 1, end, declared_variables)
            match token_type:
                case TokenType.AND:
                    return ConjunctionNode(left_ast, right_ast)
                case TokenType.OR:
                    return DisjunctionNode(left_ast, right_ast)
                case _:
                    raise NotImplementedError(f"Unknown binary operator {token_type}")

    def parse_prefix(self, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        token = self._tokens[start]
        token_type = token.type

        if token_type.is_atom_op:
            return self.parse_atom_node(token_type, start, end)
        elif token_type.is_unary_op:
            return self.parse_unary_node(token_type, start, end, declared_variables)
        elif token_type.is_binary_op:
            return self.parse_binary_node(start, end, declared_variables)
        else:
            raise ASTParserError(
                f"unknown token '{token}'",
                start,
                end,
                "Consider using an operator from the help page below"
            )

    def parse_atom_node(self, token_type: TokenType, start: int, end: int) -> ASTNode:
        if start != end:
            raise ASTParserError(
                f"expected no arguments",
                start + 1,
                end,
                f"Consider removing the arguments after '{token_type.value}'"
            )
        match token_type:
            case TokenType.TRUE:
                return TrueNode()
            case TokenType.FREE:
                return FreeNode()
            case TokenType.CROSSING:
                return CrossingSegmentNode()
            case _:
                raise NotImplementedError(f"Unknown atom operator {token_type}")

    def parse_unary_node(self, token_type: TokenType, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        if start == end:
            raise ASTParserError(
                f"expected exactly one argument",
                start,
                end,
                f"Consider defining the operator like '{token_type.value}{{arg}}'"
            )

        if token_type in {TokenType.NEGATION, TokenType.NEGATION_SHORT}:
            return NegationNode(self.parse_ast_rec(start + 1, end, declared_variables))
        else:
            match token_type:
                case TokenType.CLAIM:
                    return ClaimNode(self.parse_car_argument(token_type, start + 1, end, declared_variables))
                case TokenType.RESERVE:
                    return ReserveNode(self.parse_car_argument(token_type, start + 1, end, declared_variables))
                case _:
                    raise NotImplementedError(f"Unknown unary operator {token_type}")

    def parse_binary_node(self, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        token = self._tokens[start]
        token_type = token.type

        if token_type.is_quantor_op:
            help_message = f"Consider defining {token_type.value} like '{token_type.value} c: ...'"
            literal = None if start >= end else self._tokens[start + 1]
            if literal is None or literal.type != TokenType.LITERAL:
                raise ASTParserError(
                    "expected variable name",
                    start,
                    start + 1,
                    help_message
                )
            variable = literal.value()
            if variable in map(lambda car: car.name, self._cars):
                raise ASTParserError(
                    f"'{variable}' is a car name",
                    start + 1,
                    start + 1,
                    "Consider using a different variable name"
                )
            if variable in declared_variables: raise ASTParserError(
                f"'{variable}' is declared twice in scope",
                start + 1,
                start + 1,
                "Consider using a different variable name"
            )
            colon = None if start >= end - 1 else self._tokens[start + 2]
            if colon is None or colon.type != TokenType.COLON:
                raise ASTParserError(
                    "expected ':' after variable",
                    min(start + 2, end),
                    max(start + 2, end),
                    help_message
                )
            new_declared_variables = declared_variables.copy()
            new_declared_variables.append(variable)
            match token_type:
                case TokenType.EXITS:
                    return ExistsNode(variable, self.parse_ast_rec(start + 3, end, new_declared_variables))
                case TokenType.FORALL:
                    return ForallNode(variable, self.parse_ast_rec(start + 3, end, new_declared_variables))
                case _:
                    raise NotImplementedError(f"Unknown quantor operator {token_type}")
        else:
            # first operand
            arg1_start = start + 1
            arg1_end = self.find_closing_argument_index(arg1_start, end)
            operand1 = self.parse_expression_argument(arg1_start, arg1_end, declared_variables)
            # second operand
            arg2_start = arg1_end + 1
            arg2_end = self.find_closing_argument_index(arg2_start, end)
            operand2 = self.parse_expression_argument(arg2_start, arg2_end, declared_variables)

            match token_type:
                case TokenType.H_CHOP:
                    return HorizontalChopNode(operand1, operand2)
                case TokenType.V_CHOP:
                    return VerticalChopNode(operand2, operand1)
                case _:
                    raise NotImplementedError(f"Unknown binary operator {token_type}")

    def find_closing_argument_index(self, start_index: int, end_index: int) -> int:
        if start_index >= end_index:
            raise ASTParserError(
                "expected arguments here",
                min(start_index, end_index + 1),
                start_index,
                "Consider adding an argument like '{arg}'"
            )

        parentheses_depth = 0
        for i in range(start_index, end_index + 1):
            token = self._tokens[i]
            if token.type == TokenType.L_CURLY:
                parentheses_depth += 1
            elif token.type == TokenType.R_CURLY:
                parentheses_depth -= 1
                if parentheses_depth == 0:
                    return i
        raise ASTParserError(
            "unbalanced curly braces",
            start_index,
            end_index,
            "Consider adding '}'"
        )

    def parse_expression_argument(self, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        if self._tokens[start].type != TokenType.L_CURLY:
            raise ASTParserError(
                "argument must start by '}'",
                start,
                end
            )

        if self._tokens[end].type != TokenType.R_CURLY:
            raise ASTParserError(
                "argument must end in '}'",
                start,
                end
            )

        return self.parse_ast_rec(start + 1, end - 1, declared_variables)

    def parse_car_argument(self, token_type: TokenType, start: int, end: int,
                           declared_variables: list[str]) -> CarResolve:
        if self._tokens[start].type != TokenType.L_CURLY:
            raise ASTParserError(
                "argument must start by '}'",
                start,
                end
            )

        if self._tokens[end].type != TokenType.R_CURLY:
            raise ASTParserError(
                "argument must end in '}'",
                start,
                end
            )

        if start + 1 != end - 1:
            raise ASTParserError(
                "expected exactly one literal token",
                start,
                end,
                f"Consider defining the operator like '{token_type.value}{{name}}'"
            )

        return self.parse_car(start + 1, declared_variables)

    def parse_car(self, index: int, declared_variables: list[str]):
        token = self._tokens[index]
        value = token.value()
        if value is None:
            raise ASTParserError(
                "expected literal token",
                index,
                index,
                "Use letters to refer to cars or variables"
            )

        # check if value is a car
        for car in self._cars:
            if car.name == value:
                return ConstantCarResolve(car)

        # value is not a car, try to resolve it as a variable
        if value in declared_variables:
            return VariableCarResolve(value)

        available_cars = list(map(lambda car: car.name, self._cars))
        available_variables = declared_variables

        help_msg = f"Consider referring to one of {available_cars} (cars)"
        if len(available_variables) > 0:
            help_msg += f" or {available_variables} (vars)"

        raise ASTParserError(
            f"'{value}' neither refers to a car nor a variable",
            index,
            index,
            help_msg
        )


class ASTParserError(Exception):
    def __init__(self, reason: str, scope_start: int, scope_end: int, help: str | None = None):
        super().__init__(reason)
        self.reason = reason
        self.help = help
        self.scope_start = scope_start
        self.scope_end = scope_end
