from pse.umlsl_editor.src.model.entities.car import Car
from pse.umlsl_editor.src.query.ast.ast import ASTNode
from pse.umlsl_editor.src.query.ast.car_resolve import ConstantCarResolve, VariableCarResolve
from pse.umlsl_editor.src.query.ast.chop_node import HorizontalChopNode, VerticalChopNode
from pse.umlsl_editor.src.query.ast.claim_node import ClaimNode
from pse.umlsl_editor.src.query.ast.crossing_node import CrossingSegmentNode
from pse.umlsl_editor.src.query.ast.equality_node import EqualityCarNode
from pse.umlsl_editor.src.query.ast.free_node import FreeNode
from pse.umlsl_editor.src.query.ast.logic_node import ConjunctionNode, DisjunctionNode, NegationNode, TrueNode
from pse.umlsl_editor.src.query.ast.quantor_node import ExistsNode
from pse.umlsl_editor.src.query.ast.reserve_node import ReserveNode
from pse.umlsl_editor.src.query.lexer import Token, TokenType


# todo: curly braces check
class ASTParser:
    def __init__(self, tokens: list[Token], cars: list[Car]):
        self.tokens = tokens
        self.cars = cars

    def parse_ast(self):
        if not self.tokens:
            raise SyntaxError("Empty token list")
        return self.parse_ast_rec(0, len(self.tokens) - 1, [])

    def parse_ast_rec(self, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        if start > end:
            raise SyntaxError("Unexpected end of expression")

        tokens = self.tokens

        # todo: parse <phi> (Somewhere Node)

        height = 0
        split_index = -1
        min_precedence = int('inf')  # smallest int

        for i in range(start, end + 1):
            token = tokens[i]

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
            raise SyntaxError("Unbalanced parentheses: missing closing ')' or '}'")

        if split_index != -1:
            return self.parse_infix(start, end, split_index, declared_variables)

        if tokens[start].type == TokenType.L_PAREN and tokens[end].type == TokenType.R_PAREN:
            return self.parse_ast_rec(start + 1, end - 1, declared_variables)

        return self.parse_prefix(start, end, declared_variables)

    def parse_infix(self, start: int, end: int, split_index: int, declared_variables: list[str]) -> ASTNode:
        if not (0 <= start < split_index < end <= len(self.tokens) - 1):
            raise SyntaxError("Invalid infix expression: expected operator between tokens")

        token = self.tokens[split_index]
        token_type = token.type

        if token_type == TokenType.CAR_EQUALS:
            if start != split_index - 1 or end != split_index + 1:
                raise SyntaxError("Car equality requires exactly two tokens (i.e. car1 == car2)")
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
                    raise SyntaxError(f"Unknown binary operator {token_type}")

    def parse_prefix(self, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        token = self.tokens[start]
        token_type = token.type

        if token_type.is_nullary_op:
            return self.parse_nullary_node(token_type, start, end)
        elif token_type.is_unary_op:
            return self.parse_unary_node(token_type, start, end, declared_variables)
        elif token_type.is_binary_op:
            return self.parse_binary_node(start, end, declared_variables)
        else:
            raise SyntaxError(f"Unexpected token or format at {start}: {token}")

    def parse_nullary_node(self, token_type: TokenType, start: int, end: int) -> ASTNode:
        if start != end:
            raise SyntaxError(f"Nullary operator {token_type} requires no arguments")
        match token_type:
            case TokenType.TRUE:
                return TrueNode()
            case TokenType.FREE:
                return FreeNode()
            case TokenType.CROSSING:
                return CrossingSegmentNode()
            case _:
                raise NotImplementedError("Nullary node parsing not implemented yet")

    def parse_unary_node(self, token_type: TokenType, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        if start == end:
            raise SyntaxError(f"Unary operator {token_type} requires exactly one argument")

        if token_type in {TokenType.NEGATION, TokenType.NEGATION_SHORT}:
            return NegationNode(self.parse_ast_rec(start + 1, end, declared_variables))
        else:
            if start + 1 != end:
                raise SyntaxError(f"{token_type} requires exactly one argument")
            match token_type:
                case TokenType.CLAIM:
                    return ClaimNode(self.parse_car(start + 1, declared_variables))
                case TokenType.RESERVE:
                    return ReserveNode(self.parse_car(start + 1, declared_variables))
                case _:
                    raise NotImplementedError(f"Invalid unary operator {token_type}")

    def parse_binary_node(self, start: int, end: int, declared_variables: list[str]) -> ASTNode:
        token = self.tokens[start]
        token_type = token.type

        # todo: forall not parsed
        if token_type == TokenType.EXITS:
            literal = self.tokens[start + 1]
            if literal != TokenType.LITERAL:
                raise SyntaxError("Exits operator requires exactly one literal argument (i.e. \\exists c:)")
            value = literal.value
            if not value.endswith(":"):
                raise SyntaxError("Exists operator requires ':' after car-variable (i.e. \\exists c:)")
            variable = value[:-1]
            if variable in map(lambda car: car.name, self.cars):
                raise SyntaxError(f"Variable {variable} is a car name and cannot be used in an exists expression")
            if variable in declared_variables:
                raise SyntaxError(f"Variable {variable} declared twice in scope")
            new_declared_variables = declared_variables.copy()
            new_declared_variables.append(variable)
            return ExistsNode(variable, self.parse_ast_rec(start + 2, end, new_declared_variables))
        else:
            arg1_start = start + 1
            arg1_end = self.find_closing_argument_index(arg1_start, end)
            # todo: strip the curly braces
            operand1 = self.parse_ast_rec(arg1_start, arg1_end, declared_variables)
            arg2_start = arg1_end + 1
            arg2_end = self.find_closing_argument_index(arg2_start, end)
            # todo: strip the curly braces
            operand2 = self.parse_ast_rec(arg2_start, arg2_end, declared_variables)
            match token_type:
                case TokenType.H_CHOP:
                    return HorizontalChopNode(operand1, operand2)
                case TokenType.V_CHOP:
                    return VerticalChopNode(operand2, operand1)
                case _:
                    raise SyntaxError(f"Invalid binary operator {token_type}")

    def find_closing_argument_index(self, start_index: int, end_index: int) -> int:
        parentheses_depth = 0
        for i in range(start_index, end_index + 1):
            token = self.tokens[i]
            if token.type == TokenType.L_CURLY:
                parentheses_depth += 1
            elif token.type == TokenType.R_CURLY:
                parentheses_depth -= 1
                if parentheses_depth == 0:
                    return i
        raise SyntaxError("Unbalanced curly braces")

    def parse_car(self, index: int, declared_variables: list[str]):
        token = self.tokens[index]
        if token.type != TokenType.LITERAL:
            raise SyntaxError("Car expression requires a literal token")

        value = token.value

        # check if value is a car
        for car in self.cars:
            if car.name == value:
                return ConstantCarResolve(car)

        # value is not a car, try to resolve it as a variable
        if value in declared_variables:
            return VariableCarResolve(value)

        raise SyntaxError(f"Car '{value}' neither refers to a defined car nor a declared variable")
